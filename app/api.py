from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse, PlainTextResponse, HTMLResponse
from bs4 import BeautifulSoup
import requests
from pydantic import BaseModel
from .utils import save_file, ALLOWED_EXTENSIONS, embed_text, query_embeddings, allowed_file, get_task_details
from .database.db_util import get_db
from .database.schemas import UserCreate, UserLogin, PasswordResetRequest, PasswordReset
from .database.services import create_user, authenticate_user, reset_password_request, reset_password, delete_user, logout_user
from .data_ingestion.reader import read
from .tasks import process_transcript
from .auth import verify_token
from sqlalchemy.orm import Session
import json


import pandas as pd
from typing import List, Dict
import openai
import os
import uuid
import logging

# Storage for sessions, documents and embeddings
sessions: Dict[str, Dict[str, List[float]]] = {}
documents: Dict[str, Dict[str, str]] = {}

class URLRequest(BaseModel):
    url: str

router = APIRouter()

@router.post("/api/v1/initialize")
async def initialize_session():
    session_id = str(uuid.uuid4())
    sessions[session_id] = {}
    documents[session_id] = {}
    try:
        with open('.env.json') as f:
            env = json.load(f)
    except FileNotFoundError as e:
        logging.error("Environment file not found: %s", e)
        raise
    
    return JSONResponse(content={"session_id": session_id})

@router.post("/api/v1/pload-files", summary="Upload files", description="Endpoint to upload one or more files.",
             dependencies=[Depends(verify_token)])
async def upload_files(files: list[UploadFile] = File(...)):
    response_data = []
    for file in files:
        response = save_file(file)
        response_data.append(response)
    return JSONResponse(content=response_data)

@router.post("/api/v1/transcript-youtube", summary="Transcript YouTube", description="Transcript YouTube video",
             dependencies=[Depends(verify_token)])
async def transcript_youtube(request: URLRequest):
    task = process_transcript.delay(request.url)
    return JSONResponse(content={"task_id": task.id})

@router.get("/api/v1/transcript-task-status/{task_id}", summary="Get Task Status", description="Get the status of a Celery task",
             dependencies=[Depends(verify_token)])
async def get_task_status(task_id: str):
    task = process_transcript.AsyncResult(task_id)
    response = get_task_details(task)
    return JSONResponse(content=response)

@router.post("/api/v1/upload/{session_id}", summary="Upload file", description="Upload a file to the user.",
             dependencies=[Depends(verify_token)])
async def upload_file(session_id: str, file: UploadFile = File(...)):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="File type not allowed")

    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(file.file.read())

    text = read(file_location)

    embedding = embed_text(text)
    sessions[session_id][file.filename] = embedding
    documents[session_id][file.filename] = text
    os.remove(file_location)  # Clean up the uploaded file
    

    return JSONResponse(content={"embedding": embedding})


@router.post("/api/v1/query/{session_id}", summary="Query", description="Query the user.",
             dependencies=[Depends(verify_token)])
async def process_query(query_id: str, text: str = Query(...), sessionid: str = Query(...)):
    logging.info(f"Query: {query_id}")
    logging.info(f"Text: {text}")
    try:
        embedding = embed_text(text)
        return {"query_id": query_id, "sessionid": sessionid, "embedding": embedding}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/view/{session_id}/{filename}", summary="View", description="View the user's file.",
            dependencies=[Depends(verify_token)])
async def view_document(session_id: str, filename: str):
    if session_id not in documents or filename not in documents[session_id]:
        raise HTTPException(status_code=404, detail="Session or document not found")
    return PlainTextResponse(documents[session_id][filename])


@router.post("/api/v1/fetch-xml-content/{session_id}", summary="Fetch XML Content", description="Fetch XML Content",
             dependencies=[Depends(verify_token)])
async def fetch_xml_content(session_id: str, request: URLRequest):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        response = requests.get(request.url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'xml')
        text = ''.join(soup.stripped_strings)
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error fetching Site XML content: {str(e)}")
    
    embedding = embed_text(text)
    sessions[session_id][request.url] = embedding
    documents[session_id][request.url] = text

    return JSONResponse(content={"embedding": embedding, "content": text})


@router.post("/api/v1/register", summary="User Registration", description="",
             dependencies=[Depends(verify_token)])
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)

@router.post("/api/v1/login/", summary="User Login", description="",
              dependencies=[Depends(verify_token)])
def login(user: UserLogin, db: Session = Depends(get_db)):
    return authenticate_user(db, user)

@router.post("/api/v1/forgot-password/", summary="Forgot Password", description="Forgot Password", dependencies=[Depends(verify_token)])
def forgot_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    return reset_password_request(db, request)

@router.post("/api/v1/reset-password/", summary="Reset Password", description="Reset Password", dependencies=[Depends(verify_token)])
def reset_password(reset: PasswordReset, db: Session = Depends(get_db)):
    return reset_password(db, reset)

@router.delete("/api/v1/users/{email}" , summary="Delete User", description="Delete User", dependencies=[Depends(verify_token)])
def delete_user_endpoint(email: str, db: Session = Depends(get_db), token: str = Depends(authenticate_user)):
    return delete_user(db, email, token)

@router.post("/api/v1/logout/", summary="Logout", description="Logout", dependencies=[Depends(verify_token)])
def logout(token: str, db: Session = Depends(get_db)):
    return logout_user(db, token)

@router.get("/")
async def read_index():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)


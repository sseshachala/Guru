from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse, PlainTextResponse, HTMLResponse
from bs4 import BeautifulSoup
import requests
from pydantic import BaseModel
from .utils import save_file, ALLOWED_EXTENSIONS, embed_text, query_embeddings, allowed_file, getTaskStatus
from .data_ingestion.reader import read
from .tasks import process_transcript
from .auth import verify_token
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
    os.environ["OPENAI_API_KEY"] = env["OPENAI_API_KEY"]

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

@router.get("/api/v1/task-status/{task_id}", summary="Get Task Status", description="Get the status of a Celery task",
             dependencies=[Depends(verify_token)])
async def get_task_status(task_id: str):
    task = process_transcript.AsyncResult(task_id)
    response = get_task_status(task)
    return JSONResponse(content=response)

@router.post("/api/v1/upload/{session_id}")
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


@router.post("/api/v1/query/{session_id}")
async def process_query(query_id: str, text: str = Query(...), sessionid: str = Query(...)):
    logging.info(f"Query: {query_id}")
    logging.info(f"Text: {text}")
    try:
        embedding = embed_text(text)
        return {"query_id": query_id, "sessionid": sessionid, "embedding": embedding}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/view/{session_id}/{filename}")
async def view_document(session_id: str, filename: str):
    if session_id not in documents or filename not in documents[session_id]:
        raise HTTPException(status_code=404, detail="Session or document not found")
    return PlainTextResponse(documents[session_id][filename])


@router.post("/api/v1/fetch-xml-content/{session_id}")
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

@router.get("/")
async def read_index():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)


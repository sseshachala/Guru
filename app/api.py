from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse, HTMLResponse

from pydantic import BaseModel
from .utils import save_file, ALLOWED_EXTENSIONS, embed_text, query_embeddings, allowed_file
from .reader import read_pdf, read_docx, read_txt, read_xlsx
from .auth import verify_token

from PyPDF2 import PdfReader
import docx
import pandas as pd
from typing import List, Dict
import openai
import os
import uuid

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
    if task.state == "PENDING":
        response = {
            "state": task.state,
            "current": 0,
            "total": 1,
            "status": "Pending..."
        }
    elif task.state != "FAILURE":
        if isinstance(task.info, dict):
            response = {
                "state": task.state,
                "current": task.info.get("current", 0),
                "total": task.info.get("total", 1),
                "status": task.info.get("status", ""),
                "result": task.info.get("result") if "result" in task.info else None
            }
        else:
            response = {
                "state": task.state,
                "current": 0,
                "total": 1,
                "status": str(task.info),
            }
    else:
        response = {
            "state": task.state,
            "current": 1,
            "total": 1,
            "status": str(task.info),  # this is the exception raised
        }
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

    if file.filename.endswith(".pdf"):
        text = read_pdf(file_location)
    elif file.filename.endswith(".docx"):
        text = read_docx(file_location)
    elif file.filename.endswith(".txt"):
        text = read_txt(file_location)
    elif file.filename.endswith(".xlsx"):
        text = read_xlsx(file_location)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    embedding = embed_text(text)
    sessions[session_id][file.filename] = embedding
    documents[session_id][file.filename] = text
    os.remove(file_location)  # Clean up the uploaded file

    return JSONResponse(content={"embedding": embedding})

@router.post("/api/v1/query/{session_id}")
async def query_text(session_id: str, filename: str, query: str):
    if session_id not in sessions or filename not in sessions[session_id]:
        raise HTTPException(status_code=404, detail="Session or file not found")
    
    embedding = sessions[session_id][filename]
    answer = query_embeddings(embedding, query)
    return JSONResponse(content={"answer": answer})

@router.get("/api/v1/view/{session_id}/{filename}")
async def view_document(session_id: str, filename: str):
    if session_id not in documents or filename not in documents[session_id]:
        raise HTTPException(status_code=404, detail="Session or document not found")
    return PlainTextResponse(documents[session_id][filename])

@router.get("/")
async def read_index():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)


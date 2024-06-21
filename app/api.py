from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from .utils import save_file, get_api_key, download_yt, transcript_yt
from .tasks import process_transcript
from .auth import verify_token

class URLRequest(BaseModel):
    url: str

router = APIRouter()

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
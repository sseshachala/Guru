from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from .utils import save_file, get_api_key, download_yt, transcript_yt
from .auth import verify_token

class URLRequest(BaseModel):
    url: str

router = APIRouter()

@router.post("/upload-files", summary="Upload files", description="Endpoint to upload one or more files.",
             dependencies=[Depends(verify_token)])
async def upload_files(files: list[UploadFile] = File(...)):
    response_data = []
    for file in files:
        response = save_file(file)
        response_data.append(response)
    return JSONResponse(content=response_data)

@router.post("/transcript-youtube", summary="Transcript YouTube", description="Transcript YouTube video",
             dependencies=[Depends(verify_token)])
async def transcript_youtube(request: URLRequest):
    response = transcript_yt(download_yt(request.url))
    return JSONResponse(content=response)

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from .utils import save_file, get_api_key, transcript_yt, download_yt

class URLRequest(BaseModel):
    url: str
router = APIRouter()

@router.post("/api/upload-files", summary="Upload files", description="Endpoint to upload one or more files.",
             dependencies=[Depends(get_api_key)])
async def upload_files(files: list[UploadFile] = File(...)):
    response_data = []
    for file in files:
        response = save_file(file)
        response_data.append(response)
    return JSONResponse(content=response_data)


@router.post("/api/transcript-youtube", summary="Transcripyt Youtube", description="Transcript Youtube video",
             dependencies=[Depends(get_api_key)])
async def transcript_youtube(request: URLRequest):
    response_data = []
    response = transcript_yt(download_yt(request.url))
    response_data.append(response)
    return JSONResponse(content=response_data)

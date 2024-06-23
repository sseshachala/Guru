import logging
import os
from pathlib import Path
import shutil
from fastapi import UploadFile, Depends, HTTPException
from fastapi.security.api_key import APIKeyHeader
import json
from typing import List, Dict
import re
import os
from pytube import YouTube
import moviepy.editor as mp
from openai import OpenAI




# Load API key from .env.json file
with open(os.path.join(os.path.dirname(__file__), '..', '.env.json')) as f:
    config = json.load(f)

API_KEY = config["API_KEY"]
API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx', 'xlsx'}


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return api_key

def save_file(file: UploadFile):
    file_path = UPLOAD_DIR / file.filename
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"File {file.filename} uploaded successfully with MIME type {file.content_type}.")
        return {"filename": file.filename, "content_type": file.content_type, "message": "File uploaded successfully"}
    except Exception as e:
        logger.error(f"Error uploading file {file.filename}: {e}")
        return {"filename": file.filename, "message": f"An error occurred while uploading the file: {str(e)}"}

def get_youtube_id(url):
    # Define the regex pattern for extracting the video ID
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    
    # Search for the pattern in the URL
    match = re.search(pattern, url)
    
    # If a match is found, return the video ID
    if match:
        return match.group(1)
    else:
        return None

def download_yt(url):
    yt = YouTube(url)
    unique_file_name = get_youtube_id(url)
    logging.info(f"Downloading {unique_file_name}")
    file_name = '/tmp/' + unique_file_name + '.mp4'
    # Select the best audio stream
    audio_stream = yt.streams.filter(only_audio=True).first()

    # Download the audio stream to a temporary file
    audio_stream.download(filename=file_name)
    logging.info("file downloaded")
    # Convert the downloaded file to MP3
    clip = mp.AudioFileClip(file_name)
    mp3_file = "/tmp/" + unique_file_name + ".mp3"
    clip.write_audiofile(mp3_file)

    logging.info("MP3 downloaded")

    # Remove the temporary MP4 file
    clip.close()
    return mp3_file
            

def transcript_yt(filepath):
    # Create OpenAI Connection
    client = OpenAI()
    client.api_key  = os.environ['OPENAI_API_KEY']
    audio_file= open(filepath, "rb")
    logging.info("transcripting")
    transcript = client.audio.transcriptions.create(
                model="whisper-1",

                file=audio_file,
                language="en",
                prompt="Can you interpret,explain, add a metaphor and summarize",
                response_format="text"
                )
    return transcript


def embed_text(text: str) -> List[float]:
    client = OpenAI()
    client.api_key  = os.environ['OPENAI_API_KEY']
    response = client.embeddings.create(input=text, model="text-embedding-ada-002")
    logging.info(response)
    # Ensure response has the expected structure
    if hasattr(response, 'data') and isinstance(response.data, list) and len(response.data) > 0:
        embedding_obj = response.data[0]
        if hasattr(embedding_obj, 'embedding'):
            return embedding_obj.embedding
        else:
            raise ValueError("No 'embedding' attribute found in the first element of 'data'.")
    else:
        raise ValueError("Invalid response structure: " + str(response))

def query_embeddings(embedding: List[float], query: str) -> str:
    client = OpenAI()
    client.api_key  = os.environ['OPENAI_API_KEY']
    response = client.Completion.create(
        model="text-davinci-003",
        prompt=f"Answer the question based on the following embedding: {embedding}. Question: {query}",
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Example usage
# url = 'https://www.youtube.com/watch?v=5hMgUbmrENM'
# video_id = get_youtube_id(url)

# print(transcript_yt(download_yt(url)))

# print(f'The video ID is: {video_id}')
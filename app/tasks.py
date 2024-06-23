from celery_app import celery_app
from .utils import download_yt, transcript_yt
import logging

@celery_app.task(name="app.tasks.process_transcript")
def process_transcript(url):
    audio_file = download_yt(url)
    if audio_file:
        transcript = transcript_yt(audio_file)
        if transcript:
            logging.info(f"Transcription successful. {transcript}")
            return transcript
        else:
            print("Transcription failed or returned empty.")
            return None 
    else:
        logging.error("Try with a shorter video length")
        return None

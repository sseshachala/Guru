from celery_app import celery_app
from .utils import download_yt, transcript_yt

@celery_app.task(name="app.tasks.process_transcript")
def process_transcript(url):
    audio_file = download_yt(url)
    return transcript_yt(audio_file)

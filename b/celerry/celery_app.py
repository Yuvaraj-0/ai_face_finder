from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

celery = Celery(
    "face_finder",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["celerry.tasks"],   # <-- Add this
)
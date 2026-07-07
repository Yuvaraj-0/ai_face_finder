import logging
import requests

from celerry.celery_app import celery
from services.face_service import FaceService
from services.qdrant_service import QdrantService

logger = logging.getLogger(__name__)

face_service = FaceService()


@celery.task(name="process_uploaded_image")
def process_uploaded_image(job):

    logger.info("=" * 80)
    logger.info("CELERY TASK STARTED")

    try:

        image_id = job["image_id"]
        event_id = job["event_id"]
        photographer_id = job["photographer_id"]
        image_url = job["cloudinary_url"]

        logger.info("Downloading Image...")

        response = requests.get(image_url)

        if response.status_code != 200:
            logger.error("Failed to download image")
            return

        image_bytes = response.content

        logger.info("Image Downloaded")

        #
        # Detect Faces
        #
        faces = face_service.detect_faces(image_bytes)

        logger.info("Faces Found : %s", len(faces))

        #
        # Generate embedding for every face
        #
        for index, face in enumerate(faces):

            logger.info("Processing Face %s", index + 1)

            embedding = face_service.generate_embedding(face)

            logger.info("Embedding Length : %s", len(embedding))

            #
            # Save into Qdrant
            #
            QdrantService.save_embedding(
                image_id=image_id,
                event_id=event_id,
                photographer_id=photographer_id,
                embedding=embedding,
                # face_index=index
            )

            logger.info("Face %s Saved", index + 1)
            
    except Exception as e:
        logger.exception("Task Failed")
        logger.exception(e)
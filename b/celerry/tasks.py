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

        logger.info("Image ID: %s", image_id)
        logger.info("Event ID: %s", event_id)
        logger.info("Photographer ID: %s", photographer_id)

        logger.info("Downloading Image...")

        response = requests.get(
            image_url,
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(
                f"Failed to download image. Status: {response.status_code}"
            )

        image_bytes = response.content

        logger.info(
            "Image Downloaded. Size: %s bytes",
            len(image_bytes)
        )

        # Convert bytes → OpenCV image
        image = face_service.bytes_to_image(image_bytes)

        logger.info(
            "Image converted successfully. Shape: %s",
            image.shape
        )

        # Detect faces
        faces = face_service.detect_faces(image)

        logger.info(
            "Faces Found: %s",
            len(faces)
        )

        # No face → nothing to embed
        if len(faces) == 0:

            logger.warning(
                "No face detected. Embedding will NOT be saved to Qdrant."
            )

            return {
                "success": False,
                "reason": "no_face_detected",
                "image_id": image_id
            }

        # Generate embedding for every face
        for index, face in enumerate(faces):

            logger.info(
                "Processing Face %s",
                index + 1
            )

            # Face → 512D embedding
            embedding = face_service.generate_embedding(face)

            logger.info(
                "Embedding Length: %s",
                len(embedding)
            )

            # Save embedding to Qdrant
            logger.info(
                "Saving Face %s to Qdrant...",
                index + 1
            )

            QdrantService.save_embedding(
                image_id=image_id,
                event_id=event_id,
                photographer_id=photographer_id,
                embedding=embedding,
            )

            logger.info(
                "Face %s Saved to Qdrant",
                index + 1
            )

        logger.info("CELERY TASK COMPLETED")

        return {
            "success": True,
            "image_id": image_id,
            "faces_processed": len(faces)
        }

    except Exception:
        logger.exception("TASK FAILED")
        raise
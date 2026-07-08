from core import db
from fastapi import UploadFile, HTTPException
from services.face_service import face_service
from models.photo import Image
from services.photo_service import PhotoService
from services.qdrant_service import qdrant_service
from sqlalchemy.orm import Session
class SearchService:
    
    @staticmethod
    async def process_search(
        file: UploadFile,
        event_id: str,
        db: Session
    ):

        if file.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(
                status_code=400,
                detail="Only JPG and PNG images are allowed."
            )

        image_bytes = await file.read()

        image = face_service.bytes_to_image(image_bytes)

        faces = face_service.detect_faces(image)

        if len(faces) == 0:
            raise HTTPException(
                status_code=400,
                detail="No face detected"
            )

        if len(faces) > 1:
            raise HTTPException(
                status_code=400,
                detail="Multiple faces detected"
            )

        embedding = face_service.generate_embedding(faces[0])

        results = qdrant_service.search(
            embedding=embedding,
            event_id=event_id
        )

        if not results.points:
            return {
                "success": True,
                "matches": []
            }

        score_map = {
            point.payload["image_id"]: point.score
            for point in results.points
        }

        image_ids = list(score_map.keys())

        images = PhotoService.get_images_by_ids(
            db=db,
            image_ids=image_ids
        )

        response = []

        for image in images:
            response.append({
                "image_id": image.id,
                "image_url": image.cloudinary_secure_url, 
                "score": score_map[image.id]
            })

        return {
            "success": True,
            "matches": response
        }
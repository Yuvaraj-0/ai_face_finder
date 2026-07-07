from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from typing import List, Optional, Dict, Any
from services.cloudinary_service import CloudinaryService
from core.db import settings

from models.photo import Image


class PhotoService:

    @staticmethod
    def get_images_by_ids(
        db: Session,
        image_ids: list[str]
    ):
        images = (
            db.query(Image)
            .filter(Image.id.in_(image_ids))
            .all()
        )

        return images

class ImageService:
    def __init__(self, db: Session):
        self.db = db
        self.cloudinary = CloudinaryService()
    @staticmethod
    def get_images_by_ids(
        db: Session,
        image_ids: list[str]
    ):
        images = (
            db.query(Image)
            .filter(Image.id.in_(image_ids))
            .all()
        )

        return images
    async def upload_single_image(
        self,
        file: UploadFile,
        event_id: str,
        photographer_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Upload a single image
        Returns: dict with image data and cloudinary info
        """
        # Validate file
        await self._validate_file(file)
        
        # Upload to Cloudinary
        upload_result = await self.cloudinary.upload_image(
            file, 
            event_id, 
            photographer_id
        )
        
        if not upload_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Cloudinary upload failed: {upload_result.get('error')}"
            )
        
        # Prepare image data for database
        image_data = {
            "event_id": event_id,
            "photographer_id": photographer_id,
            "original_filename": file.filename,
            "file_size": upload_result["bytes"],
            "mime_type": file.content_type or "image/jpeg",
            "cloudinary_public_id": upload_result["public_id"],
            "cloudinary_url": upload_result["url"],
            "cloudinary_secure_url": upload_result["secure_url"],
            "width": upload_result.get("width"),
            "height": upload_result.get("height"),
            "format": upload_result.get("format"),
            "metadata": metadata or {}
        }
        
        return image_data
    
    async def upload_multiple_images(
        self,
        files: List[UploadFile],
        event_id: str,
        photographer_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> tuple[List[Dict], List[Dict[str, str]]]:
        """
        Upload multiple images
        Returns: (successful_images_data, errors)
        """
        # Validate all files
        for file in files:
            await self._validate_file(file)
        
        # Upload to Cloudinary
        upload_results = await self.cloudinary.upload_multiple_images(
            files, 
            event_id, 
            photographer_id
        )
        
        # Process results
        saved_images_data = []
        errors = []
        
        for idx, result in enumerate(upload_results):
            if result["success"]:
                image_data = {
                    "event_id": event_id,
                    "photographer_id": photographer_id,
                    "original_filename": files[idx].filename if idx < len(files) else "unknown",
                    "file_size": result["bytes"],
                    "mime_type": files[idx].content_type or "image/jpeg",
                    "cloudinary_public_id": result["public_id"],
                    "cloudinary_url": result["url"],
                    "cloudinary_secure_url": result["secure_url"],
                    "width": result.get("width"),
                    "height": result.get("height"),
                    "format": result.get("format"),
                    "metadata": metadata or {}
                }
                saved_images_data.append(image_data)
            else:
                errors.append({
                    "file": files[idx].filename if idx < len(files) else "unknown",
                    "error": result.get("error", "Unknown error")
                })
        
        return saved_images_data, errors
    
    async def delete_image(self, cloudinary_public_id: str) -> bool:
        """Delete a single image from Cloudinary"""
        return await self.cloudinary.delete_image(cloudinary_public_id)
    
    async def delete_multiple_images(self, cloudinary_public_ids: List[str]) -> Dict[str, bool]:
        """Delete multiple images from Cloudinary"""
        return await self.cloudinary.delete_multiple_images(cloudinary_public_ids)
    
    async def _validate_file(self, file: UploadFile):
        """Validate uploaded file"""
        # Check file size
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)
        
        if size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds {settings.MAX_FILE_SIZE // (1024*1024)}MB limit"
            )
        
        # Check file extension
        if file.filename:
            extension = file.filename.split(".")[-1].lower()
            if extension not in settings.ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"File type not allowed. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="File has no name"
            )
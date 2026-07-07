from email import errors
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
import json
from uuid import uuid4
from core.db import settings
from datetime import date
from database.db import get_db
# Import your services
from services.photo_service import ImageService
from services.cloudinary_service import CloudinaryService
from celerry.tasks import process_uploaded_image
# Import your models and schemas (you'll implement these)
from models.event import Event
from models.photo import Image
from schemas.photo import (
    ImageResponse, 
    DeleteResponse, 
    BulkImageUploadResponse,
    ImageListResponse
)
import logging
import traceback
from fastapi import Request

router = APIRouter(prefix="/api/v1", tags=["images"])
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# ============ SINGLE IMAGE UPLOAD ============
@router.post("/images/upload", response_model=ImageResponse)
async def upload_single_image(
    request: Request,
    file: UploadFile = File(...),
    event_id: str = Form(...),
    photographer_id: str = Form(...),
    metadata: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        logger.info("=" * 80)
        logger.info("UPLOAD IMAGE REQUEST RECEIVED")

        logger.info(f"Method: {request.method}")
        logger.info(f"URL: {request.url}")

        logger.info("Headers:")
        for key, value in request.headers.items():
            logger.info(f"{key}: {value}")

        logger.info("Incoming Form Data")
        logger.info(f"event_id: {event_id}")
        logger.info(f"photographer_id: {photographer_id}")
        logger.info(f"metadata: {metadata}")

        logger.info("File Details")
        logger.info(f"filename: {file.filename}")
        logger.info(f"content_type: {file.content_type}")

        contents = await file.read()

        logger.info(f"file_size: {len(contents)} bytes")

        file.file.seek(0)

        service = ImageService(db)

        metadata_dict = json.loads(metadata) if metadata else None

        logger.info("Checking event...")

        event = db.query(Event).filter(
            Event.id == event_id,
            Event.photographer_id == photographer_id
        ).first()

        logger.info(f"Event found: {event is not None}")

        if not event:
            logger.error("Event not found")
            raise HTTPException(
                status_code=404,
                detail="Event not found or you don't have permission"
            )

        image_count = db.query(Image).filter(
            Image.event_id == event_id
        ).count()

        logger.info(f"Current image count: {image_count}")

        if image_count >= settings.MAX_IMAGES_PER_EVENT:
            logger.error("Image limit exceeded")
            raise HTTPException(
                status_code=400,
                detail=f"Maximum {settings.MAX_IMAGES_PER_EVENT} images per event"
            )

        logger.info("Uploading image to Cloudinary...")

        image_data = await service.upload_single_image(
            file=file,
            event_id=event_id,
            photographer_id=photographer_id,
            metadata=metadata_dict
        )

        logger.info("Cloudinary upload successful")
        logger.info(image_data)

        db_image = Image(
            id=str(uuid4()),
            event_id=image_data["event_id"],
            photographer_id=image_data["photographer_id"],
            original_filename=image_data["original_filename"],
            file_size=image_data["file_size"],
            mime_type=image_data["mime_type"],
            cloudinary_public_id=image_data["cloudinary_public_id"],
            cloudinary_url=image_data["cloudinary_url"],
            cloudinary_secure_url=image_data["cloudinary_secure_url"],
            width=image_data["width"],
            height=image_data["height"],
            format=image_data["format"],
            metadata=image_data["metadata"]
        )

        logger.info("Saving image to database...")

        db.add(db_image)
        db.commit()
        db.refresh(db_image)

        logger.info("Image saved successfully")
        logger.info("=" * 80)

        return db_image

    except HTTPException:
        raise

    except Exception as e:
        logger.error("=" * 80)
        logger.error("UPLOAD FAILED")
        logger.error(str(e))
        logger.error(traceback.format_exc())
        logger.error("=" * 80)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# ============ MULTIPLE IMAGES UPLOAD ============
@router.post("/images/upload-multiple", response_model=BulkImageUploadResponse)
async def upload_multiple_images(
    files: List[UploadFile] = File(...),
    event_id: str = Form(...),
    photographer_id: str = Form(...),
    metadata: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        logger.info("=" * 80)
        logger.info("MULTIPLE IMAGE UPLOAD REQUEST RECEIVED")

        logger.info("event_id: %s", event_id)
        logger.info("photographer_id: %s", photographer_id)
        logger.info("metadata: %s", metadata)

        logger.info("Number of files received: %s", len(files))

        for i, file in enumerate(files):
            logger.info("-" * 50)
            logger.info("File #%s", i + 1)
            logger.info("filename: %s", file.filename)
            logger.info("content_type: %s", file.content_type)

            contents = await file.read()
            logger.info("size: %s bytes", len(contents))
            file.file.seek(0)

        # Parse metadata
        logger.info("Parsing metadata...")
        metadata_dict = json.loads(metadata) if metadata else None
        logger.info("Parsed metadata: %s", metadata_dict)

        logger.info("Checking event...")
        event = db.query(Event).filter(
            Event.id == event_id,
            Event.photographer_id == photographer_id
        ).first()

        logger.info("Event found: %s", event is not None)

        if not event:
            logger.error("Event not found")
            raise HTTPException(
                status_code=404,
                detail="Event not found or you don't have permission"
            )

        current_count = db.query(Image).filter(
            Image.event_id == event_id
        ).count()

        logger.info("Current image count: %s", current_count)

        if current_count + len(files) > settings.MAX_IMAGES_PER_EVENT:
            logger.error("Image limit exceeded")
            raise HTTPException(
                status_code=400,
                detail=f"Cannot upload {len(files)} images"
            )

        logger.info("Uploading to Cloudinary...")

        service = ImageService(db)

        saved_images_data, errors = await service.upload_multiple_images(
            files=files,
            event_id=event_id,
            photographer_id=photographer_id,
            metadata=metadata_dict
        )

        logger.info("Cloudinary upload finished")
        logger.info("Successful uploads: %s", len(saved_images_data))
        logger.info("Errors: %s", errors)

        saved_images = []

        for image_data in saved_images_data:
            logger.info("Saving image:")
            logger.info(image_data)

            db_image = Image(
                id=str(uuid4()),
                event_id=image_data["event_id"],
                photographer_id=image_data["photographer_id"],
                original_filename=image_data["original_filename"],
                file_size=image_data["file_size"],
                mime_type=image_data["mime_type"],
                cloudinary_public_id=image_data["cloudinary_public_id"],
                cloudinary_url=image_data["cloudinary_url"],
                cloudinary_secure_url=image_data["cloudinary_secure_url"],
                width=image_data["width"],
                height=image_data["height"],
                format=image_data["format"],
                metadata=image_data["metadata"]
            )

            db.add(db_image)
            saved_images.append(db_image)

        logger.info("Committing database...")

        if saved_images:
            db.commit()

            for img in saved_images:
                db.refresh(img)

        logger.info("Database commit successful")
# ----------------------------------
        logger.info("=" * 80)
        logger.info("SENDING JOBS TO CELERY")

        for img in saved_images:

            job = {
                "image_id": img.id,
                "event_id": img.event_id,
                "photographer_id": img.photographer_id,
                "cloudinary_url": img.cloudinary_secure_url
            }

            logger.info("Sending Job")
            logger.info(job)

            process_uploaded_image.delay(job)

        logger.info("ALL JOBS SENT")
        logger.info("=" * 80)
        response = BulkImageUploadResponse(
            success_count=len(saved_images),
            failed_count=len(errors),
            images=saved_images,
            errors=errors if errors else None
        )

        logger.info("Returning response")
        logger.info(response.model_dump())

        logger.info("=" * 80)

        return response

    except Exception as e:
        logger.error("=" * 80)
        logger.error("UPLOAD MULTIPLE FAILED")
        logger.error(str(e))
        logger.error(traceback.format_exc())
        logger.error("=" * 80)
        raise

# ============ DELETE SINGLE IMAGE ============
@router.delete("/images/{image_id}", response_model=DeleteResponse)
async def delete_single_image(
    image_id: str,
    photographer_id: str,
    db: Session = Depends(get_db)  # Your database dependency
):
    """
    Delete a single image
    
    - **image_id**: UUID of the image
    - **photographer_id**: UUID of the photographer (for authorization)
    """
    # Get image from database (you implement this)
    image = db.query(Image).filter(
        Image.id == image_id,
        Image.photographer_id == photographer_id
    ).first()
    
    if not image:
        raise HTTPException(
            status_code=404,
            detail="Image not found or you don't have permission"
        )
    
    # Delete from Cloudinary
    service = ImageService(db)
    deleted = await service.delete_image(image.cloudinary_public_id)
    
    if not deleted:
        # Log error but continue with DB deletion
        print(f"Warning: Failed to delete from Cloudinary: {image.cloudinary_public_id}")
    
    # Delete from database (you implement this)
    db.delete(image)
    db.commit()
    
    return DeleteResponse(
        success=True,
        message="Image deleted successfully"
    )


# ============ DELETE MULTIPLE IMAGES (Bulk) ============
@router.delete("/images/bulk-delete", response_model=DeleteResponse)
async def delete_multiple_images(
    image_ids: List[str] = Query(..., description="List of image IDs to delete"),
    photographer_id: str = Query(..., description="Photographer ID for authorization"),
    db: Session = Depends(get_db)  # Your database dependency
):
    """
    Delete multiple images
    
    - **image_ids**: List of image UUIDs
    - **photographer_id**: UUID of the photographer (for authorization)
    """
    # Get images from database (you implement this)
    images = db.query(Image).filter(
        Image.id.in_(image_ids),
        Image.photographer_id == photographer_id
    ).all()
    
    if not images:
        raise HTTPException(
            status_code=404,
            detail="No images found or you don't have permission"
        )
    
    # Delete from Cloudinary
    service = ImageService(db)
    public_ids = [img.cloudinary_public_id for img in images]
    delete_results = await service.delete_multiple_images(public_ids)
    
    # Delete from database (you implement this)
    for image in images:
        db.delete(image)
    
    db.commit()
    
    return DeleteResponse(
        success=True,
        message=f"Deleted {len(images)} images",
        deleted_count=len(images)
    )


# ============ DELETE ALL EVENT IMAGES ============
@router.delete("/events/{event_id}/images", response_model=DeleteResponse)
async def delete_event_images(
    event_id: str,
    photographer_id: str,
    db: Session = Depends(get_db)  # Your database dependency
):
    """
    Delete all images for an event
    
    - **event_id**: UUID of the event
    - **photographer_id**: UUID of the photographer (for authorization)
    """
    # Get all images for event (you implement this)
    images = db.query(Image).filter(
        Image.event_id == event_id,
        Image.photographer_id == photographer_id
    ).all()
    
    if not images:
        raise HTTPException(
            status_code=404,
            detail="No images found for this event"
        )
    
    # Delete from Cloudinary
    service = ImageService(db)
    public_ids = [img.cloudinary_public_id for img in images]
    await service.delete_multiple_images(public_ids)
    
    # Delete from database (you implement this)
    for image in images:
        db.delete(image)
    
    db.commit()
    
    return DeleteResponse(
        success=True,
        message=f"Deleted {len(images)} images",
        deleted_count=len(images)
    )


# ============ GET EVENT IMAGES ============
@router.get("/events/{event_id}/images", response_model=ImageListResponse)
async def get_event_images(
    event_id: str,
    photographer_id: str = Query(..., description="Photographer ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)  # Your database dependency
):
    """
    Get all images for an event with pagination
    
    - **event_id**: UUID of the event
    - **photographer_id**: UUID of the photographer (for authorization)
    - **skip**: Number of records to skip
    - **limit**: Number of records to return
    """
    # Verify event exists (you implement this)
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.photographer_id == photographer_id
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found or you don't have permission"
        )
    
    # Get images from database (you implement this)
    images = db.query(Image).filter(
        Image.event_id == event_id
    ).offset(skip).limit(limit).all()
    
    total = db.query(Image).filter(Image.event_id == event_id).count()
    
    return ImageListResponse(
        total=total,
        images=images
    )


# ============ GET SINGLE IMAGE DETAILS ============
@router.get("/images/{image_id}", response_model=ImageResponse)
async def get_image_details(
    image_id: str,
    photographer_id: str = Query(..., description="Photographer ID"),
    db: Session = Depends(get_db)  # Your database dependency
):
    """
    Get details of a specific image
    
    - **image_id**: UUID of the image
    - **photographer_id**: UUID of the photographer (for authorization)
    """
    # Get image from database (you implement this)
    image = db.query(Image).filter(
        Image.id == image_id,
        Image.photographer_id == photographer_id
    ).first()
    
    if not image:
        raise HTTPException(
            status_code=404,
            detail="Image not found or you don't have permission"
        )
    
    return image


# ============ GET IMAGES COUNT ============
@router.get("/events/{event_id}/images/count")
async def get_images_count(
    event_id: str,
    photographer_id: str = Query(..., description="Photographer ID"),
    db: Session = Depends(get_db)  # Your database dependency
):
    """
    Get total number of images for an event
    
    - **event_id**: UUID of the event
    - **photographer_id**: UUID of the photographer (for authorization)
    """
    # Verify event exists (you implement this)
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.photographer_id == photographer_id
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found or you don't have permission"
        )
    
    # Get count from database (you implement this)
    count = db.query(Image).filter(Image.event_id == event_id).count()
    
    return {"event_id": event_id, "total_images": count}


# ============ GET IMAGES BY PHOTOGRAPHER ============
@router.get("/images/photographer/{photographer_id}", response_model=ImageListResponse)
async def get_photographer_images(
    photographer_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)  # Your database dependency
):
    """
    Get all images uploaded by a photographer
    
    - **photographer_id**: UUID of the photographer
    - **skip**: Number of records to skip
    - **limit**: Number of records to return
    """
    # Get images from database (you implement this)
    images = db.query(Image).filter(
        Image.photographer_id == photographer_id
    ).offset(skip).limit(limit).all()
    
    total = db.query(Image).filter(
        Image.photographer_id == photographer_id
    ).count()
    
    return ImageListResponse(
        total=total,
        images=images
    )


# ============ GET TRANSFORMED IMAGE URL ============
@router.post("/images/transform/{image_id}")
async def get_transformed_image(
    image_id: str,
    photographer_id: str = Query(..., description="Photographer ID"),
    width: Optional[int] = Query(None, ge=1),
    height: Optional[int] = Query(None, ge=1),
    crop: str = Query("fit", regex="^(fit|crop|thumb|scale|fill|limit|pad)$"),
    gravity: str = Query("auto"),
    quality: Optional[int] = Query(None, ge=1, le=100),
    db: Session = Depends(get_db)  # Your database dependency
):
    """
    Get transformed version of an image
    
    - **image_id**: UUID of the image
    - **photographer_id**: UUID of the photographer (for authorization)
    - **width**: Desired width
    - **height**: Desired height
    - **crop**: Crop mode (fit, crop, thumb, scale, fill, limit, pad)
    - **gravity**: Gravity for cropping (auto, face, center, etc.)
    - **quality**: Image quality (1-100)
    """
    # Get image from database (you implement this)
    image = db.query(Image).filter(
        Image.id == image_id,
        Image.photographer_id == photographer_id
    ).first()
    
    if not image:
        raise HTTPException(
            status_code=404,
            detail="Image not found or you don't have permission"
        )
    
    # Build transformation
    transformations = {}
    if width:
        transformations["width"] = width
    if height:
        transformations["height"] = height
    if crop:
        transformations["crop"] = crop
    if gravity:
        transformations["gravity"] = gravity
    if quality:
        transformations["quality"] = quality
    
    # Get transformed URL
    service = ImageService(db)
    transformed_url = service.cloudinary.get_transformed_url(
        image.cloudinary_public_id,
        transformations
    )
    
    return {
        "original_url": image.cloudinary_url,
        "transformed_url": transformed_url,
        "transformations": transformations
    }
from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session

from database.db import get_db
from services.search_service import SearchService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["Search"])



@router.post("/")
async def search(
    file: UploadFile = File(...),
    event_id: str = Form(...),
    db: Session = Depends(get_db)
):
    logger.info(f"Filename: {file.filename}")
    logger.info(f"Content-Type: {file.content_type}")
    logger.info(f"Event ID: {event_id}")

    return await SearchService.process_search(
        file=file,
        event_id=event_id,
        db=db
    )
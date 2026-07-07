from fastapi import APIRouter, UploadFile, File, Form
from fastapi import Depends, Session
from database.db import get_db

from services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Search"])


@router.post("/search")
async def search(
    file: UploadFile = File(...),
    event_id: int = Form(...),
    db: Session = Depends(get_db)
):
    return await SearchService.process_search(
        file=file,
        event_id=event_id,
        db=db
    )
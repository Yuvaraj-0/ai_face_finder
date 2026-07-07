from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.db import get_db
from schemas.event import (
    EventCreate,
    EventUpdate,
    EventResponse,
)
from services.event_service import EventService
from models.event import Event
# Replace this with your JWT authentication dependency
from dependencies.auth import get_current_photographer
from dependencies.event import get_event_or_404
router = APIRouter(
    prefix="/events",
    tags=["Events"],
)
print("Event router loaded")
@router.post(
    "/event",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_photographer),
):

    return EventService.create_event(
        db=db,
        event_data=event_data,
        photographer_id=current_user.id,
    )


@router.get(
    "/{event_id}",
    response_model=EventResponse,
    status_code=status.HTTP_200_OK,
)
def get_event(
    event: Event = Depends(get_event_or_404),
):
    return event

@router.put("/{event_id}")
def update_event(
    event_data: EventUpdate,
    event: Event = Depends(get_event_or_404),
    db: Session = Depends(get_db),
):
    return EventService.update_event(
        db,
        event,
        event_data,
    )


@router.delete("/{event_id}")
def delete_event(
    event: Event = Depends(get_event_or_404),
    db: Session = Depends(get_db),
):
    EventService.delete_event(
        db,
        event,
    )
from fastapi import Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from database.db import get_db
from models.event import Event
from dependencies.auth import get_current_photographer
from models.user import User


def get_event_or_404(
    event_id: str = Path(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_photographer),
) -> Event:

    event = (
        db.query(Event)
        .filter(
            Event.id == event_id,
            Event.photographer_id == current_user.id,
        )
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    return event
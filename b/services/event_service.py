from sqlalchemy.orm import Session

from models.event import Event
from schemas.event import EventCreate, EventUpdate


class EventService:

    @staticmethod
    def create_event(
        db: Session,
        event_data: EventCreate,
        photographer_id: str,
    ) -> Event:

        event = Event(
            name=event_data.name,
            description=event_data.description,
            event_date=event_data.event_date,
            photographer_id=photographer_id,
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        return event

    @staticmethod
    def get_all_events(
        db: Session,
        photographer_id: str,
    ) -> list[Event]:

        return (
            db.query(Event)
            .filter(Event.photographer_id == photographer_id)
            .order_by(Event.created_at.desc())
            .all()
        )

    @staticmethod
    def get_event_by_id(
        db: Session,
        event_id: str,
        photographer_id: str,
    ) -> Event | None:

        return (
            db.query(Event)
            .filter(
                Event.id == event_id,
                Event.photographer_id == photographer_id,
            )
            .first()
        )

    @staticmethod
    def update_event(
        db: Session,
        event: Event,
        event_data: EventUpdate,
    ) -> Event:

        update_data = event_data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(event, key, value)

        db.commit()
        db.refresh(event)

        return event

    @staticmethod
    def delete_event(
        db: Session,
        event: Event,
    ) -> None:

        db.delete(event)
        db.commit()
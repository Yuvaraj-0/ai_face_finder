from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class EventCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Event name"
    )

    description: Optional[str] = Field(
        None,
        max_length=500
    )

    event_date: date


class EventUpdate(BaseModel):
    name: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100
    )

    description: Optional[str] = Field(
        None,
        max_length=500
    )

    event_date: Optional[date] = None


class EventResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    event_date: date
    photographer_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
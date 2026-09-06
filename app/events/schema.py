from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.events.enums import EventStatus


class EventCreate(BaseModel):
    venue_id: UUID
    title: str
    description: str | None = None
    starts_at: datetime


class EventUpdate(BaseModel):
    venue_id: UUID | None = None
    title: str | None = None
    description: str | None = None
    starts_at: datetime | None = None


class EventResponse(BaseModel):
    id: UUID
    venue_id: UUID
    organizer_id: UUID
    title: str
    description: str | None
    starts_at: datetime
    status: EventStatus

    model_config = ConfigDict(from_attributes=True)


class EventPage(BaseModel):
    items: list[EventResponse]
    next_cursor: UUID | None

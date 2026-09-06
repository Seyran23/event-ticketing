from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.events.enums import EventStatus
from app.events.model import Event


async def get_by_id(db: AsyncSession, event_id: UUID) -> Event | None:
    return await db.get(Event, event_id)


async def list_published(db: AsyncSession, cursor: UUID | None, limit: int) -> list[Event]:
    query = (
        select(Event).where(Event.status == EventStatus.PUBLISHED).order_by(Event.id).limit(limit)
    )
    if cursor is not None:
        query = query.where(Event.id > cursor)

    result = await db.execute(query)
    return list(result.scalars().all())


async def list_by_organizer(
    db: AsyncSession, organizer_id: UUID, cursor: UUID | None, limit: int
) -> list[Event]:
    query = select(Event).where(Event.organizer_id == organizer_id).order_by(Event.id).limit(limit)
    if cursor is not None:
        query = query.where(Event.id > cursor)

    result = await db.execute(query)
    return list(result.scalars().all())


async def create(
    db: AsyncSession,
    organizer_id: UUID,
    venue_id: UUID,
    title: str,
    description: str | None,
    starts_at: datetime,
) -> Event:
    event = Event(
        organizer_id=organizer_id,
        venue_id=venue_id,
        title=title,
        description=description,
        starts_at=starts_at,
    )

    db.add(event)
    await db.flush()

    return event


async def update(db: AsyncSession, event: Event, changes: dict[str, Any]) -> Event:
    for field, value in changes.items():
        setattr(event, field, value)

    await db.flush()

    return event

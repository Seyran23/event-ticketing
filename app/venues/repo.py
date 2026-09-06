from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.venues.model import Venue


async def get_by_id(db: AsyncSession, venue_id: UUID) -> Venue | None:
    return await db.get(Venue, venue_id)


async def list_all(db: AsyncSession, cursor: UUID | None, limit: int) -> list[Venue]:
    query = select(Venue).order_by(Venue.id).limit(limit)
    if cursor is not None:
        query = query.where(Venue.id > cursor)

    result = await db.execute(query)
    return list(result.scalars().all())


async def list_by_organizer(
    db: AsyncSession, organizer_id: UUID, cursor: UUID | None, limit: int
) -> list[Venue]:
    query = select(Venue).where(Venue.organizer_id == organizer_id).order_by(Venue.id).limit(limit)
    if cursor is not None:
        query = query.where(Venue.id > cursor)

    result = await db.execute(query)
    return list(result.scalars().all())


async def create(db: AsyncSession, organizer_id: UUID, name: str, address: str) -> Venue:
    venue = Venue(organizer_id=organizer_id, name=name, address=address)

    db.add(venue)
    await db.flush()

    return venue

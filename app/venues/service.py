from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schema import TokenPayload
from app.core.enums import Role
from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.pagination import MAX_PAGE_SIZE
from app.venues import repo
from app.venues.schema import VenueCreate, VenuePage, VenueResponse


async def create_venue(db: AsyncSession, organizer_id: UUID, data: VenueCreate) -> VenueResponse:
    venue = await repo.create(db, organizer_id, data.name, data.address)
    await db.commit()

    return VenueResponse.model_validate(venue)


async def get_venue(db: AsyncSession, venue_id: UUID, current_user: TokenPayload) -> VenueResponse:
    venue = await repo.get_by_id(db, venue_id)

    if venue is None:
        raise NotFoundError("Venue not found.")

    if venue.organizer_id != UUID(current_user.sub) and current_user.role != Role.ADMIN:
        raise ForbiddenError("You do not have access to this venue.")

    return VenueResponse.model_validate(venue)


async def list_venues(
    db: AsyncSession,
    current_user: TokenPayload,
    cursor: UUID | None = None,
    limit: int = 20,
) -> VenuePage:
    limit = min(limit, MAX_PAGE_SIZE)

    if current_user.role == Role.ADMIN:
        venues = await repo.list_all(db, cursor, limit + 1)
    else:
        venues = await repo.list_by_organizer(db, UUID(current_user.sub), cursor, limit + 1)

    next_cursor = venues[limit - 1].id if len(venues) > limit else None
    page = venues[:limit]

    return VenuePage(
        items=[VenueResponse.model_validate(venue) for venue in page],
        next_cursor=next_cursor,
    )

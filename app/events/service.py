from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schema import TokenPayload
from app.core.enums import Role
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.core.pagination import MAX_PAGE_SIZE
from app.events import repo
from app.events.enums import EventStatus
from app.events.model import Event
from app.events.schema import EventCreate, EventPage, EventResponse, EventUpdate
from app.venues import repo as venues_repo


def _is_owner_or_admin(event: Event, current_user: TokenPayload) -> bool:
    return event.organizer_id == UUID(current_user.sub) or current_user.role == Role.ADMIN


async def create_event(db: AsyncSession, organizer_id: UUID, data: EventCreate) -> EventResponse:
    venue = await venues_repo.get_by_id(db, data.venue_id)

    if venue is None:
        raise NotFoundError("Venue not found.")

    if venue.organizer_id != organizer_id:
        raise ForbiddenError("You do not own this venue.")

    event = await repo.create(
        db, organizer_id, data.venue_id, data.title, data.description, data.starts_at
    )
    await db.commit()

    return EventResponse.model_validate(event)


async def get_event(
    db: AsyncSession, event_id: UUID, current_user: TokenPayload | None
) -> EventResponse:
    event = await repo.get_by_id(db, event_id)
   
    if event is None:
        raise NotFoundError("Event not found.")

    is_visible = event.status == EventStatus.PUBLISHED or (
        current_user is not None and _is_owner_or_admin(event, current_user)
    )
    
    if not is_visible:
        raise NotFoundError("Event not found.")

    return EventResponse.model_validate(event)


async def list_events(db: AsyncSession, cursor: UUID | None = None, limit: int = 20) -> EventPage:
    limit = min(limit, MAX_PAGE_SIZE)

    events = await repo.list_published(db, cursor, limit + 1)

    next_cursor = events[limit - 1].id if len(events) > limit else None
    page = events[:limit]

    return EventPage(
        items=[EventResponse.model_validate(event) for event in page],
        next_cursor=next_cursor,
    )


async def update_event(
    db: AsyncSession, event_id: UUID, current_user: TokenPayload, data: EventUpdate
) -> EventResponse:
    event = await repo.get_by_id(db, event_id)

    if event is None:
        raise NotFoundError("Event not found.")

    if not _is_owner_or_admin(event, current_user):
        raise ForbiddenError("You do not have access to this event.")

    changes = data.model_dump(exclude_unset=True)

    if "venue_id" in changes:
        venue = await venues_repo.get_by_id(db, changes["venue_id"])
        if venue is None:
            raise NotFoundError("Venue not found.")
        if venue.organizer_id != event.organizer_id:
            raise ForbiddenError("You do not own this venue.")

    event = await repo.update(db, event, changes)
    await db.commit()

    return EventResponse.model_validate(event)


async def publish_event(
    db: AsyncSession, event_id: UUID, current_user: TokenPayload
) -> EventResponse:
    event = await repo.get_by_id(db, event_id)
    
    if event is None:
        raise NotFoundError("Event not found.")

    if not _is_owner_or_admin(event, current_user):
        raise ForbiddenError("You do not have access to this event.")

    if event.status != EventStatus.DRAFT:
        raise ConflictError("Only a draft event can be published.")

    event = await repo.update(db, event, {"status": EventStatus.PUBLISHED})
    await db.commit()

    return EventResponse.model_validate(event)


async def cancel_event(
    db: AsyncSession, event_id: UUID, current_user: TokenPayload
) -> EventResponse:
    event = await repo.get_by_id(db, event_id)
    
    if event is None:
        raise NotFoundError("Event not found.")

    if not _is_owner_or_admin(event, current_user):
        raise ForbiddenError("You do not have access to this event.")

    if event.status == EventStatus.CANCELLED:
        raise ConflictError("Event is already cancelled.")

    event = await repo.update(db, event, {"status": EventStatus.CANCELLED})
    await db.commit()

    return EventResponse.model_validate(event)

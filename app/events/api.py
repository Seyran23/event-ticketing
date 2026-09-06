from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schema import TokenPayload
from app.core.database import get_db
from app.core.dependencies import get_optional_current_user, require_role
from app.core.enums import Role
from app.events import service as events_service
from app.events.schema import EventCreate, EventPage, EventResponse, EventUpdate

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    data: EventCreate,
    current_user: TokenPayload = Depends(require_role(Role.ORGANIZER)),
    db: AsyncSession = Depends(get_db),
) -> EventResponse:
    return await events_service.create_event(db, UUID(current_user.sub), data)


@router.get("", response_model=EventPage)
async def list_events(
    cursor: UUID | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> EventPage:
    return await events_service.list_events(db, cursor, limit)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: UUID,
    current_user: TokenPayload | None = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
) -> EventResponse:
    return await events_service.get_event(db, event_id, current_user)


@router.patch("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: UUID,
    data: EventUpdate,
    current_user: TokenPayload = Depends(require_role(Role.ORGANIZER, Role.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> EventResponse:
    return await events_service.update_event(db, event_id, current_user, data)


@router.post("/{event_id}/publish", response_model=EventResponse)
async def publish_event(
    event_id: UUID,
    current_user: TokenPayload = Depends(require_role(Role.ORGANIZER, Role.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> EventResponse:
    return await events_service.publish_event(db, event_id, current_user)


@router.delete("/{event_id}", response_model=EventResponse)
async def cancel_event(
    event_id: UUID,
    current_user: TokenPayload = Depends(require_role(Role.ORGANIZER, Role.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> EventResponse:
    return await events_service.cancel_event(db, event_id, current_user)

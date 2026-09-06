from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schema import TokenPayload
from app.core.database import get_db
from app.core.dependencies import require_role
from app.core.enums import Role
from app.venues import service as venues_service
from app.venues.schema import VenueCreate, VenuePage, VenueResponse

router = APIRouter(prefix="/venues", tags=["venues"])


@router.post("", response_model=VenueResponse, status_code=status.HTTP_201_CREATED)
async def create_venue(
    data: VenueCreate,
    current_user: TokenPayload = Depends(require_role(Role.ORGANIZER, Role.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> VenueResponse:
    return await venues_service.create_venue(db, UUID(current_user.sub), data)


@router.get("", response_model=VenuePage)   
async def list_venues(
    cursor: UUID | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    current_user: TokenPayload = Depends(require_role(Role.ORGANIZER, Role.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> VenuePage:
    return await venues_service.list_venues(db, current_user, cursor, limit)


@router.get("/{venue_id}", response_model=VenueResponse)
async def get_venue(
    venue_id: UUID,
    current_user: TokenPayload = Depends(require_role(Role.ORGANIZER, Role.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> VenueResponse:
    return await venues_service.get_venue(db, venue_id, current_user)

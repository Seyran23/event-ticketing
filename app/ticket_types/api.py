from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schema import TokenPayload
from app.core.database import get_db
from app.core.dependencies import get_optional_current_user, require_role
from app.core.enums import Role
from app.ticket_types import service as ticket_types_service
from app.ticket_types.schema import TicketTypeCreate, TicketTypeResponse, TicketTypeUpdate

router = APIRouter(tags=["ticket-types"])


@router.post(
    "/events/{event_id}/ticket-types",
    response_model=TicketTypeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_ticket_type(
    event_id: UUID,
    data: TicketTypeCreate,
    current_user: TokenPayload = Depends(require_role(Role.ORGANIZER)),
    db: AsyncSession = Depends(get_db),
) -> TicketTypeResponse:
    return await ticket_types_service.create_ticket_type(db, event_id, UUID(current_user.sub), data)


@router.get("/events/{event_id}/ticket-types", response_model=list[TicketTypeResponse])
async def list_ticket_types(
    event_id: UUID,
    current_user: TokenPayload | None = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[TicketTypeResponse]:
    return await ticket_types_service.list_ticket_types(db, event_id, current_user)


@router.patch("/ticket-types/{ticket_type_id}", response_model=TicketTypeResponse)
async def update_ticket_type(
    ticket_type_id: UUID,
    data: TicketTypeUpdate,
    current_user: TokenPayload = Depends(require_role(Role.ORGANIZER)),
    db: AsyncSession = Depends(get_db),
) -> TicketTypeResponse:
    return await ticket_types_service.update_ticket_type(
        db, ticket_type_id, UUID(current_user.sub), data
    )

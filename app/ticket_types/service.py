from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schema import TokenPayload
from app.core.enums import Role
from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.events import repo as events_repo
from app.events.enums import EventStatus
from app.events.model import Event
from app.ticket_types import repo
from app.ticket_types.exceptions import SoldOutError
from app.ticket_types.model import TicketType
from app.ticket_types.schema import TicketTypeCreate, TicketTypeResponse, TicketTypeUpdate


def _is_owner_or_admin(event: Event, current_user: TokenPayload) -> bool:
    return event.organizer_id == UUID(current_user.sub) or current_user.role == Role.ADMIN


async def create_ticket_type(
    db: AsyncSession, event_id: UUID, organizer_id: UUID, data: TicketTypeCreate
) -> TicketTypeResponse:
    event = await events_repo.get_by_id(db, event_id)

    if event is None:
        raise NotFoundError("Event not found.")

    if event.organizer_id != organizer_id:
        raise ForbiddenError("You do not have access to this event.")

    ticket_type = await repo.create(
        db, event_id, data.name, data.price_cents, data.currency, data.total_quantity
    )
    await db.commit()

    return TicketTypeResponse.model_validate(ticket_type)


async def list_ticket_types(
    db: AsyncSession, event_id: UUID, current_user: TokenPayload | None
) -> list[TicketTypeResponse]:
    event = await events_repo.get_by_id(db, event_id)

    if event is None:
        raise NotFoundError("Event not found.")

    is_visible = event.status == EventStatus.PUBLISHED or (
        current_user is not None and _is_owner_or_admin(event, current_user)
    )

    if not is_visible:
        raise NotFoundError("Event not found.")

    ticket_types = await repo.list_by_event(db, event_id)

    return [TicketTypeResponse.model_validate(tt) for tt in ticket_types]


async def update_ticket_type(
    db: AsyncSession, ticket_type_id: UUID, organizer_id: UUID, data: TicketTypeUpdate
) -> TicketTypeResponse:
    ticket_type = await repo.get_by_id(db, ticket_type_id)

    if ticket_type is None:
        raise NotFoundError("Ticket type not found.")

    event = await events_repo.get_by_id(db, ticket_type.event_id)

    if event is None or event.organizer_id != organizer_id:
        raise ForbiddenError("You do not have access to this ticket type.")

    changes = data.model_dump(exclude_unset=True)

    new_total = changes.get("total_quantity", ticket_type.total_quantity)
    new_available = changes.get("available_quantity", ticket_type.available_quantity)

    if new_available > new_total:
        raise ValidationError("available_quantity cannot exceed total_quantity.")

    ticket_type = await repo.update(db, ticket_type, changes)
    await db.commit()

    return TicketTypeResponse.model_validate(ticket_type)


async def reserve_inventory(db: AsyncSession, ticket_type_id: UUID, quantity: int) -> TicketType:
    # FIX: without this, a caller passing quantity=0 or a negative number
    # sails straight past the `available_quantity < quantity` check below
    # (always false once quantity <= 0, since available_quantity is never
    # negative) and then ADDS to available_quantity instead of subtracting
    # -- manufacturing free inventory. Verified this by actually calling
    # reserve_inventory(..., -5) against a real row: available_quantity
    # went from 10 to 15 instead of raising. This guards the function's own
    # contract regardless of whether every future caller remembers to
    # validate quantity first.
    if quantity <= 0:
        raise ValueError("quantity must be a positive integer.")

    ticket_type = await repo.get_by_id_for_update(db, ticket_type_id)
    if ticket_type is None:
        raise NotFoundError("Ticket type not found.")

    if ticket_type.available_quantity < quantity:
        raise SoldOutError(f"Only {ticket_type.available_quantity} left, requested {quantity}.")

    ticket_type = await repo.update(
        db, ticket_type, {"available_quantity": ticket_type.available_quantity - quantity}
    )
    return ticket_type

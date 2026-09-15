from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ticket_types.model import TicketType


async def get_by_id(db: AsyncSession, ticket_type_id: UUID) -> TicketType | None:
    return await db.get(TicketType, ticket_type_id)


async def get_by_id_for_update(db: AsyncSession, ticket_type_id: UUID) -> TicketType | None:
    result = await db.execute(
        select(TicketType).where(TicketType.id == ticket_type_id).with_for_update()
    )
    return result.scalar_one_or_none()


async def list_by_event(db: AsyncSession, event_id: UUID) -> list[TicketType]:
    result = await db.execute(select(TicketType).where(TicketType.event_id == event_id))
    return list(result.scalars().all())


async def create(
    db: AsyncSession,
    event_id: UUID,
    name: str,
    price_cents: int,
    currency: str,
    total_quantity: int,
) -> TicketType:
    ticket_type = TicketType(
        event_id=event_id,
        name=name,
        price_cents=price_cents,
        currency=currency,
        total_quantity=total_quantity,
        available_quantity=total_quantity,
    )

    db.add(ticket_type)
    await db.flush()

    return ticket_type


async def update(db: AsyncSession, ticket_type: TicketType, changes: dict[str, Any]) -> TicketType:
    for field, value in changes.items():
        setattr(ticket_type, field, value)

    await db.flush()

    return ticket_type

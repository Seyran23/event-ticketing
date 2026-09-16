from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import literal, select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationError
from app.orders.model import Order, OrderItem


async def get_by_id(db: AsyncSession, order_id: UUID) -> Order | None:
    return await db.get(Order, order_id)


async def list_items_by_order(db: AsyncSession, order_id: UUID) -> list[OrderItem]:
    result = await db.execute(select(OrderItem).where(OrderItem.order_id == order_id))
    return list(result.scalars().all())


async def list_items_by_order_ids(db: AsyncSession, order_ids: list[UUID]) -> list[OrderItem]:
    if not order_ids:
        return []

    result = await db.execute(select(OrderItem).where(OrderItem.order_id.in_(order_ids)))
    return list(result.scalars().all())


async def list_by_user(
    db: AsyncSession, user_id: UUID, cursor: UUID | None, limit: int
) -> list[Order]:
    query = select(Order).where(Order.user_id == user_id)
    query = query.order_by(Order.created_at.desc(), Order.id.desc()).limit(limit)

    if cursor is not None:
        cursor_order = await get_by_id(db, cursor)

        if cursor_order is None or cursor_order.user_id != user_id:
            raise ValidationError("Invalid cursor.")

        query = query.where(
            tuple_(Order.created_at, Order.id)
            < tuple_(literal(cursor_order.created_at), literal(cursor_order.id))
        )

    result = await db.execute(query)
    return list(result.scalars().all())


async def create(db: AsyncSession, user_id: UUID, total_cents: int, expires_at: datetime) -> Order:
    order = Order(user_id=user_id, total_cents=total_cents, expires_at=expires_at)

    db.add(order)
    await db.flush()

    return order


async def create_item(
    db: AsyncSession, order_id: UUID, ticket_type_id: UUID, quantity: int, unit_price_cents: int
) -> OrderItem:
    item = OrderItem(
        order_id=order_id,
        ticket_type_id=ticket_type_id,
        quantity=quantity,
        unit_price_cents=unit_price_cents,
    )

    db.add(item)
    await db.flush()

    return item


async def update(db: AsyncSession, order: Order, changes: dict[str, Any]) -> Order:
    for field, value in changes.items():
        setattr(order, field, value)

    await db.flush()

    return order

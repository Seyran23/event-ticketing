from collections import defaultdict
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.core.pagination import MAX_PAGE_SIZE
from app.events import repo as events_repo
from app.events.enums import EventStatus
from app.orders import repo
from app.orders.constants import HOLD_DURATION_MINUTES
from app.orders.enums import OrderStatus
from app.orders.model import Order, OrderItem
from app.orders.schema import OrderCreate, OrderItemResponse, OrderPage, OrderResponse
from app.ticket_types import repo as ticket_types_repo
from app.ticket_types import service as ticket_types_service
from app.ticket_types.model import TicketType


async def _build_order_responses(db: AsyncSession, orders: list[Order]) -> list[OrderResponse]:
    order_ids = [order.id for order in orders]
    items = await repo.list_items_by_order_ids(db, order_ids)

    ticket_type_ids = list({item.ticket_type_id for item in items})
    ticket_types = await ticket_types_repo.list_by_ids(db, ticket_type_ids)
    ticket_type_names = {tt.id: tt.name for tt in ticket_types}

    items_by_order: dict[UUID, list[OrderItem]] = defaultdict(list)
    for item in items:
        items_by_order[item.order_id].append(item)

    responses = []
    for order in orders:
        item_responses = [
            OrderItemResponse(
                id=item.id,
                ticket_type_id=item.ticket_type_id,
                ticket_type_name=ticket_type_names.get(item.ticket_type_id, "Unknown"),
                quantity=item.quantity,
                unit_price_cents=item.unit_price_cents,
            )
            for item in items_by_order[order.id]
        ]
        responses.append(
            OrderResponse(
                id=order.id,
                user_id=order.user_id,
                status=order.status,
                total_cents=order.total_cents,
                created_at=order.created_at,
                expires_at=order.expires_at,
                items=item_responses,
            )
        )

    return responses


async def create_order(db: AsyncSession, user_id: UUID, data: OrderCreate) -> OrderResponse:
    sorted_items = sorted(data.items, key=lambda item: item.ticket_type_id)

    reserved: dict[UUID, TicketType] = {}
    try:
        for item in sorted_items:
            ticket_type = await ticket_types_repo.get_by_id(db, item.ticket_type_id)
            if ticket_type is None:
                raise NotFoundError("Ticket type not found.")

            event = await events_repo.get_by_id(db, ticket_type.event_id)
            if event is None or event.status != EventStatus.PUBLISHED:
                raise NotFoundError("Ticket type not found.")

            reserved[item.ticket_type_id] = await ticket_types_service.reserve_inventory(
                db, item.ticket_type_id, item.quantity
            )
    except Exception:
        await db.rollback()
        raise

    total_cents = sum(
        reserved[item.ticket_type_id].price_cents * item.quantity for item in sorted_items
    )
    expires_at = datetime.now(UTC) + timedelta(minutes=HOLD_DURATION_MINUTES)

    order = await repo.create(db, user_id, total_cents, expires_at)

    for item in sorted_items:
        await repo.create_item(
            db,
            order.id,
            item.ticket_type_id,
            item.quantity,
            reserved[item.ticket_type_id].price_cents,
        )

    await db.commit()

    responses = await _build_order_responses(db, [order])
    return responses[0]


async def get_order(db: AsyncSession, order_id: UUID, user_id: UUID) -> OrderResponse:
    order = await repo.get_by_id(db, order_id)

    if order is None or order.user_id != user_id:
        raise NotFoundError("Order not found.")

    responses = await _build_order_responses(db, [order])
    return responses[0]


async def list_user_orders(
    db: AsyncSession, user_id: UUID, cursor: UUID | None, limit: int
) -> OrderPage:
    limit = min(limit, MAX_PAGE_SIZE)

    orders = await repo.list_by_user(db, user_id, cursor, limit + 1)
    next_cursor = orders[limit - 1].id if len(orders) > limit else None
    page = orders[:limit]

    return OrderPage(items=await _build_order_responses(db, page), next_cursor=next_cursor)


async def cancel_order(db: AsyncSession, order_id: UUID, user_id: UUID) -> OrderResponse:
    order = await repo.get_by_id(db, order_id)

    if order is None or order.user_id != user_id:
        raise NotFoundError("Order not found.")

    if order.status != OrderStatus.PENDING:
        raise ConflictError("Only a pending order can be cancelled.")

    items = await repo.list_items_by_order(db, order_id)

    for item in items:
        await ticket_types_service.release_inventory(db, item.ticket_type_id, item.quantity)

    order = await repo.update(db, order, {"status": OrderStatus.CANCELLED})
    await db.commit()

    responses = await _build_order_responses(db, [order])
    return responses[0]

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schema import TokenPayload
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.orders import service as orders_service
from app.orders.schema import OrderCreate, OrderPage, OrderResponse

router = APIRouter(tags=["orders"])


@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    data: OrderCreate,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    return await orders_service.create_order(db, UUID(current_user.sub), data)


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    return await orders_service.get_order(db, order_id, UUID(current_user.sub))


@router.post("/orders/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: UUID,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    return await orders_service.cancel_order(db, order_id, UUID(current_user.sub))


@router.get("/users/me/orders", response_model=OrderPage)
async def list_my_orders(
    cursor: UUID | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrderPage:
    return await orders_service.list_user_orders(db, UUID(current_user.sub), cursor, limit)

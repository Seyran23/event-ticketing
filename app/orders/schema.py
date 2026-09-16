from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.orders.enums import OrderStatus


class OrderItemCreate(BaseModel):
    ticket_type_id: UUID
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    items: list[OrderItemCreate]

    @model_validator(mode="after")
    def validate_items(self) -> "OrderCreate":
        if not self.items:
            raise ValueError("An order must contain at least one item.")

        ticket_type_ids = [item.ticket_type_id for item in self.items]

        if len(ticket_type_ids) != len(set(ticket_type_ids)):
            raise ValueError("Duplicate ticket_type_id in order items.")

        return self


class OrderItemResponse(BaseModel):
    id: UUID
    ticket_type_id: UUID
    ticket_type_name: str
    quantity: int
    unit_price_cents: int

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: UUID
    user_id: UUID
    status: OrderStatus
    total_cents: int
    created_at: datetime
    expires_at: datetime
    items: list[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)


class OrderPage(BaseModel):
    items: list[OrderResponse]
    next_cursor: UUID | None

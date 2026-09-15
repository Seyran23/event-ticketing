from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TicketTypeCreate(BaseModel):
    name: str
    price_cents: int = Field(ge=0)
    currency: str = "USD"
    total_quantity: int = Field(gt=0)


class TicketTypeUpdate(BaseModel):
    name: str | None = None
    price_cents: int | None = Field(default=None, ge=0)
    currency: str | None = None
    total_quantity: int | None = Field(default=None, gt=0)
    available_quantity: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def check_available_not_over_total(self) -> "TicketTypeUpdate":
        if (
            self.total_quantity is not None
            and self.available_quantity is not None
            and self.available_quantity > self.total_quantity
        ):
            raise ValueError("available_quantity cannot exceed total_quantity.")
        return self


class TicketTypeResponse(BaseModel):
    id: UUID
    event_id: UUID
    name: str
    price_cents: int
    currency: str
    total_quantity: int
    available_quantity: int

    model_config = ConfigDict(from_attributes=True)

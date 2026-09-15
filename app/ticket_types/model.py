from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TicketType(Base):
    __tablename__ = "ticket_types"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    event_id: Mapped[UUID] = mapped_column(ForeignKey("events.id"), index=True)
    name: Mapped[str] = mapped_column()
    price_cents: Mapped[int] = mapped_column()
    currency: Mapped[str] = mapped_column(default="USD")
    total_quantity: Mapped[int] = mapped_column()
    available_quantity: Mapped[int] = mapped_column()

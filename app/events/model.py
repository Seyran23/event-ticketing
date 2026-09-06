from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.events.enums import EventStatus


class Event(Base):
    __tablename__ = "events"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    venue_id: Mapped[UUID] = mapped_column(ForeignKey("venues.id"), index=True)
    organizer_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column()
    description: Mapped[str | None] = mapped_column()
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[EventStatus] = mapped_column(Enum(EventStatus), default=EventStatus.DRAFT)

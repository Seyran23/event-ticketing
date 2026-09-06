from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Venue(Base):
    __tablename__ = "venues"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column()
    address: Mapped[str] = mapped_column()
    organizer_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)

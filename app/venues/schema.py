from uuid import UUID

from pydantic import BaseModel, ConfigDict


class VenueCreate(BaseModel):
    name: str
    address: str


class VenueResponse(BaseModel):
    id: UUID
    name: str
    address: str
    organizer_id: UUID

    model_config = ConfigDict(from_attributes=True)


class VenuePage(BaseModel):
    items: list[VenueResponse]
    next_cursor: UUID | None

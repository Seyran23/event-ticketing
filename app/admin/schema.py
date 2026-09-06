from typing import Literal

from app.core.enums import Role
from app.users.schema import UserCreate


class AdminUserCreate(UserCreate):
    role: Literal[Role.USER, Role.ORGANIZER]

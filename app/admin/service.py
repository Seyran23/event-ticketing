from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.schema import AdminUserCreate
from app.core.exceptions import ConflictError
from app.core.security import Security
from app.users.repo import create, get_by_email
from app.users.schema import UserResponse


async def create_user(db: AsyncSession, data: AdminUserCreate) -> UserResponse:
    existing_user = await get_by_email(db, data.email)
    if existing_user:
        raise ConflictError("Email is already registered.")

    hashed_password = Security().hash_password(data.password)

    try:
        new_user = await create(
            db, data.email, hashed_password, role=data.role, must_change_password=True
        )
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        raise ConflictError("Email is already registered.") from e

    return UserResponse.model_validate(new_user)

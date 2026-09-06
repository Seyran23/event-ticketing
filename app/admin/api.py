from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin import service as admin_service
from app.admin.schema import AdminUserCreate
from app.auth.schema import TokenPayload
from app.core.database import get_db
from app.core.dependencies import require_role
from app.core.enums import Role
from app.users.schema import UserResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: AdminUserCreate,
    current_user: TokenPayload = Depends(require_role(Role.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    return await admin_service.create_user(db, data)

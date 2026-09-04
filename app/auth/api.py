from uuid import UUID

from fastapi import APIRouter, Cookie, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import service as auth_service
from app.auth.schema import AccessTokenResponse, AuthResponse, LoginRequest, TokenPayload
from app.auth.utils.cookie import set_refresh_cookie
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import UnauthorizedError
from app.users.schema import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserCreate, response: Response, db: AsyncSession = Depends(get_db)
) -> AuthResponse:
    result = await auth_service.register_user(db, data)

    set_refresh_cookie(response=response, refresh_token=result.refresh_token)

    return AuthResponse(user=result.user, access_token=result.access_token)


@router.post("/login", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def login(
    data: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)
) -> AuthResponse:
    result = await auth_service.login_user(db, data)

    set_refresh_cookie(response=response, refresh_token=result.refresh_token)

    return AuthResponse(user=result.user, access_token=result.access_token)


@router.post("/refresh", response_model=AccessTokenResponse, status_code=status.HTTP_200_OK)
async def refresh_access_token(
    refresh_token: str | None = Cookie(default=None),
) -> AccessTokenResponse:

    if refresh_token is None:
        raise UnauthorizedError("Missing refresh token.")

    new_access_token = await auth_service.refresh(refresh_token)
    return AccessTokenResponse(access_token=new_access_token)


@router.get("/me", response_model=UserResponse)
async def me(
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:

    user = await auth_service.get_current_user_profile(db, UUID(current_user.sub))  

    return user

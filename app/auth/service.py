from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.exceptions import InvalidCredentialsError, InvalidTokenError
from app.auth.jwt import JWTService
from app.auth.schema import AuthResult, LoginRequest
from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import Security
from app.users.repo import create, get_by_email, get_by_id
from app.users.schema import UserCreate, UserResponse


async def register_user(db: AsyncSession, data: UserCreate) -> AuthResult:
    existing_user = await get_by_email(db, data.email)

    if existing_user:
        raise ConflictError("Email is already registered.")

    hashed_password = Security().hash_password(data.password)

    try:
        new_user = await create(db, data.email, hashed_password)
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        raise ConflictError("Email is already registered.") from e

    jwt_service = JWTService()
    access_token = jwt_service.create_access_token(new_user.id, new_user.role)
    refresh_token = jwt_service.create_refresh_token(new_user.id, new_user.role)

    return AuthResult(
        user=UserResponse.model_validate(new_user),
        access_token=access_token,
        refresh_token=refresh_token,
    )


async def login_user(db: AsyncSession, data: LoginRequest) -> AuthResult:
    user = await get_by_email(db, data.email)
    if not user:
        raise InvalidCredentialsError()

    is_correct_password = Security().verify_password(data.password, user.password_hash)

    if not is_correct_password:
        raise InvalidCredentialsError()

    jwt_service = JWTService()
    access_token = jwt_service.create_access_token(user.id, user.role)
    refresh_token = jwt_service.create_refresh_token(user.id, user.role)

    return AuthResult(
        user=UserResponse.model_validate(user),
        access_token=access_token,
        refresh_token=refresh_token,
    )


async def get_current_user_profile(db: AsyncSession, user_id: UUID) -> UserResponse:
    user = await get_by_id(db, user_id)
    
    if user is None:
        raise NotFoundError("User not found.")

    return UserResponse.model_validate(user)


async def refresh(refresh_token: str) -> str:
    jwt_service = JWTService()
    payload = jwt_service.decode(refresh_token)

    if payload.type != "refresh":
        raise InvalidTokenError("Provided token is not a refresh token.")

    return jwt_service.create_access_token(UUID(payload.sub), payload.role)

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.exceptions import InvalidTokenError
from app.auth.jwt import JWTService
from app.auth.schema import TokenPayload
from app.core.enums import Role
from app.core.exceptions import ForbiddenError, UnauthorizedError

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> TokenPayload:
    if credentials is None:
        raise UnauthorizedError("Missing bearer token.")

    payload = JWTService().decode(credentials.credentials)

    if payload.type != "access":
        raise InvalidTokenError("Provided token is not an access token.")

    return payload


async def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> TokenPayload | None:
    if credentials is None:
        return None

    return await get_current_user(credentials)


def require_role(*roles: Role):
    def checker(current_user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
        if current_user.role not in roles:
            raise ForbiddenError()
        return current_user

    return checker

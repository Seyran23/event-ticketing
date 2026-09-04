from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt

from app.auth.exceptions import InvalidTokenError
from app.auth.schema import TokenPayload
from app.core.config import settings
from app.core.enums import Role


class JWTService:
    def __init__(self):
        self.secret = settings.JWT_SECRET
        self.algorithm = settings.JWT_ALGORITHM

    def create_access_token(self, user_id: UUID, role: Role) -> str:
        payload = TokenPayload(
            sub=str(user_id),
            exp=datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            role=role,
            type="access",
        )

        return self.encode(payload)

    def create_refresh_token(self, user_id: UUID, role: Role) -> str:
        payload = TokenPayload(
            sub=str(user_id),
            exp=datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            role=role,
            type="refresh",
        )

        return self.encode(payload)

    def encode(self, payload: TokenPayload) -> str:
        return jwt.encode(
            payload.model_dump(mode="python"),
            self.secret,
            algorithm=self.algorithm,
        )

    def decode(self, token: str) -> TokenPayload:
        try:
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
            )

            return TokenPayload.model_validate(payload)

        except jwt.ExpiredSignatureError as e:
            raise InvalidTokenError("Token has expired") from e

        except jwt.InvalidTokenError as e:
            raise InvalidTokenError("Invalid token") from e

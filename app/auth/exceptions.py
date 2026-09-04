from app.core.exceptions import UnauthorizedError


class InvalidCredentialsError(UnauthorizedError):
    """Invalid email or password."""

    error_code = "invalid_credentials"


class InvalidTokenError(UnauthorizedError):
    """Invalid or expired token."""

    error_code = "invalid_token"

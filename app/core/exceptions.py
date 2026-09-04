class AppError(Exception):
    """An unexpected error occurred."""

    status_code: int = 500
    error_code: str = "internal_error"

    def __init__(self, message: str | None = None):
        self.message = message or self.__class__.__doc__ or "An error occurred"
        super().__init__(self.message)


class NotFoundError(AppError):
    """Resource not found."""

    status_code = 404
    error_code = "not_found"


class ConflictError(AppError):
    """Resource conflict."""

    status_code = 409
    error_code = "conflict"


class UnauthorizedError(AppError):
    """Authentication required."""

    status_code = 401
    error_code = "unauthorized"


class ForbiddenError(AppError):
    """You do not have permission to perform this action."""

    status_code = 403
    error_code = "forbidden"


class ValidationError(AppError):
    """Invalid input."""

    status_code = 422
    error_code = "validation_error"

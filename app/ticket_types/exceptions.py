from app.core.exceptions import ConflictError


class SoldOutError(ConflictError):
    """Not enough tickets available."""

    error_code = "sold_out"

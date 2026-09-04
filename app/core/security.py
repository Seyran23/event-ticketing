from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError


class Security:
    def __init__(self) -> None:
        self._password_hasher = PasswordHasher()

    def hash_password(self, password: str) -> str:
        return self._password_hasher.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        try:
            return self._password_hasher.verify(hashed_password, plain_password)
        except (VerifyMismatchError, VerificationError):
            return False

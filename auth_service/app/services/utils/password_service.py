from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError


class PasswordService:
    def __init__(self):
        self.password_hasher = PasswordHasher()

    def hash_password(self, password: str) -> str:
        return self.password_hasher.hash(password)

    def verify_password(self, hashed_password: str, password: str) -> bool:
        try:
            return self.password_hasher.verify(hashed_password, password)
        except (InvalidHashError, VerificationError, VerifyMismatchError):
            return False


password_service = PasswordService()

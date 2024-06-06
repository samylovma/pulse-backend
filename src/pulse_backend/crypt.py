__all__ = (
    "hash_password",
    "check_password",
)

import bcrypt


def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password=_encode_password(password), salt=bcrypt.gensalt())


def check_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(
        password=_encode_password(password),
        hashed_password=hashed_password,
    )


def _encode_password(password: str) -> bytes:
    return password.encode(encoding="utf-8")

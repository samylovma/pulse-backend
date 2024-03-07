import bcrypt


def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(
        password=password.encode(encoding="utf-8"), salt=bcrypt.gensalt()
    )


def check_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(
        password=password.encode(encoding="utf-8"),
        hashed_password=hashed_password,
    )

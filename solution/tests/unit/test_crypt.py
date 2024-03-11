from pulse_backend import crypt


def test_valid() -> None:
    hashed_password = crypt.hash_password("password123")
    assert crypt.check_password("password123", hashed_password) is True


def test_invalid() -> None:
    hashed_password = crypt.hash_password("password123")
    assert crypt.check_password("invalidpassword5", hashed_password) is False

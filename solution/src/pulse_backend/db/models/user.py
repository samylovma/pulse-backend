from sqlalchemy import BigInteger, Sequence, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):  # pylint: disable=too-few-public-methods
    id: Mapped[int] = mapped_column(
        BigInteger(), Sequence("user_id_seq"), primary_key=True, unique=True
    )
    login: Mapped[str] = mapped_column(
        String(30), primary_key=True, unique=True
    )
    email: Mapped[str] = mapped_column(String(50), unique=True)
    hashed_password: Mapped[bytes]
    country_code: Mapped[str] = mapped_column(String(2))
    is_public: Mapped[bool]
    phone: Mapped[str | None] = mapped_column(String(20), unique=True)
    image: Mapped[str | None] = mapped_column(String(200))

from datetime import datetime

from advanced_alchemy.base import (
    BigIntBase,
    CommonTableAttributes,
    UUIDBase,
    orm_registry,
)
from sqlalchemy import (
    ARRAY,
    TEXT,
    TIMESTAMP,
    ForeignKey,
    String,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(CommonTableAttributes, DeclarativeBase):
    registry = orm_registry


# We shouldn't change the schema of this table,
# so we just define it as it presented in the database.
class Country(Base):
    __tablename__ = "countries"  # type: ignore[assignment]

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None] = mapped_column(TEXT())
    alpha2: Mapped[str | None] = mapped_column(TEXT())
    alpha3: Mapped[str | None] = mapped_column(TEXT())
    region: Mapped[str | None] = mapped_column(TEXT())


class User(Base):
    login: Mapped[str] = mapped_column(String(30), primary_key=True, unique=True)
    email: Mapped[str] = mapped_column(String(50), unique=True)
    hashed_password: Mapped[bytes]
    country_code: Mapped[str] = mapped_column(String(2))
    is_public: Mapped[bool]
    phone: Mapped[str | None] = mapped_column(String(20), unique=True)
    image: Mapped[str | None] = mapped_column(String(200))


class Friend(BigIntBase):
    of_login: Mapped[str] = mapped_column(ForeignKey(User.login), primary_key=True)
    login: Mapped[str] = mapped_column(ForeignKey(User.login), primary_key=True)
    addedAt: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))


class Post(UUIDBase):
    content: Mapped[str] = mapped_column(String(1000))
    author: Mapped[str] = mapped_column(ForeignKey(User.login))
    tags: Mapped[list[str]] = mapped_column(ARRAY(String(20)))
    createdAt: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    likesCount: Mapped[int] = mapped_column(default=0)
    dislikesCount: Mapped[int] = mapped_column(default=0)

    user: Mapped[User] = relationship(lazy="joined")


class Session(UUIDBase):
    exp: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    user_login: Mapped[int] = mapped_column(ForeignKey(User.login))
    user: Mapped[User] = relationship(lazy="joined")

from advanced_alchemy.base import CommonTableAttributes, orm_registry, UUIDBase
from sqlalchemy import TEXT, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    registry = orm_registry


class Country(CommonTableAttributes, Base):
    __tablename__ = "countries"  # type: ignore[assignment]

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None] = mapped_column(TEXT())
    alpha2: Mapped[str | None] = mapped_column(TEXT())
    alpha3: Mapped[str | None] = mapped_column(TEXT())
    region: Mapped[str | None] = mapped_column(TEXT())


class User(CommonTableAttributes, Base):
    login: Mapped[str] = mapped_column(
        String(30), primary_key=True, unique=True
    )
    email: Mapped[str] = mapped_column(String(50), unique=True)
    hashedPassword: Mapped[bytes]
    countryCode: Mapped[str] = mapped_column(String(2))
    isPublic: Mapped[bool]
    phone: Mapped[str | None] = mapped_column(String(20), unique=True)
    image: Mapped[str | None] = mapped_column(String(200))


class Token(UUIDBase):
    user_login: Mapped[str] = mapped_column(ForeignKey(User.login))
    user: Mapped[User] = relationship(lazy="joined")

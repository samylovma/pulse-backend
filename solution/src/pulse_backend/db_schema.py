from advanced_alchemy.base import CommonTableAttributes
from sqlalchemy import TEXT, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    ...


class Country(CommonTableAttributes, Base):
    __tablename__ = "countries"  # type: ignore[assignment]

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(TEXT())
    alpha2: Mapped[str] = mapped_column(TEXT(), unique=True)
    alpha3: Mapped[str] = mapped_column(TEXT())
    region: Mapped[str] = mapped_column(TEXT())


class User(CommonTableAttributes, Base):
    login: Mapped[str] = mapped_column(
        String(30), primary_key=True, unique=True
    )
    email: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[bytes]
    country_code: Mapped[str] = mapped_column(ForeignKey(Country.alpha2))
    is_public: Mapped[bool]
    phone: Mapped[str | None] = mapped_column(String(20), unique=True)
    image: Mapped[str | None] = mapped_column(String(200))

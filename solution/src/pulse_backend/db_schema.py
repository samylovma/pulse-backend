from advanced_alchemy.base import CommonTableAttributes
from sqlalchemy import TEXT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    ...


class Country(CommonTableAttributes, Base):
    __tablename__ = "countries"  # type: ignore[assignment]

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(TEXT())
    alpha2: Mapped[str] = mapped_column(TEXT())
    alpha3: Mapped[str] = mapped_column(TEXT())
    region: Mapped[str] = mapped_column(TEXT())

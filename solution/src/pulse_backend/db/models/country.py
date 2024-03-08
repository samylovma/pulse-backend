# pylint: disable=unsubscriptable-object,too-few-public-methods

from sqlalchemy import TEXT
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


# We shouldn't change the schema of this table,
# so we just define it as it presented in the database.
class Country(Base):
    __tablename__ = "countries"  # type: ignore[assignment]

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None] = mapped_column(TEXT())
    alpha2: Mapped[str | None] = mapped_column(TEXT())
    alpha3: Mapped[str | None] = mapped_column(TEXT())
    region: Mapped[str | None] = mapped_column(TEXT())

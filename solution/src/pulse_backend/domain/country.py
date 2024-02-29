from typing import Annotated

from litestar.contrib.sqlalchemy.base import CommonTableAttributes
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO, SQLAlchemyDTOConfig
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
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


class CountryRepository(SQLAlchemyAsyncRepository[Country]):
    model_type = Country


CountryDTO = SQLAlchemyDTO[
    Annotated[
        Country,
        SQLAlchemyDTOConfig(
            exclude={
                "id",
            }
        ),
    ]
]

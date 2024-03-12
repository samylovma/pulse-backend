from typing import Annotated

from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO, SQLAlchemyDTOConfig

from pulse_backend.db_models import Country

CountryDTO = SQLAlchemyDTO[
    Annotated[Country, SQLAlchemyDTOConfig(exclude={"id",})]
]

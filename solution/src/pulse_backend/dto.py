from typing import Annotated

from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO, SQLAlchemyDTOConfig

from pulse_backend.db_models import Country, User

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

UserDTO = SQLAlchemyDTO[
    Annotated[
        User,
        SQLAlchemyDTOConfig(
            exclude={
                "hashed_password",
            },
            rename_strategy="camel",
        ),
    ]
]

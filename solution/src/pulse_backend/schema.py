import enum
from typing import Annotated

import pydantic
from pydantic import Field


class BaseModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)


class CountryRegion(enum.StrEnum):
    europe = "Europe"
    africa = "Africa"
    americas = "Americas"
    oceania = "Oceania"
    asia = "Asia"


class Country(BaseModel):
    name: Annotated[str, Field(max_length=100)]
    alpha2: Annotated[str, Field(max_length=2, pattern=r"[a-zA-Z]{2}")]
    alpha3: Annotated[str, Field(max_length=3, pattern=r"[a-zA-Z]{3}")]
    region: CountryRegion | str | None = None


class UserProfile(BaseModel):
    login: str
    email: str
    country_code: Annotated[str, Field(serialization_alias="countryCode")]
    is_public: Annotated[bool, Field(serialization_alias="isPublic")]
    phone: str | None
    image: str | None

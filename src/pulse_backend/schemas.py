import enum
from typing import Annotated

import pydantic
from pydantic import AfterValidator, EmailStr, Field


class BaseModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)


class CountryRegion(enum.StrEnum):
    EUROPE = "Europe"
    AFRICA = "Africa"
    AMERICAS = "Americas"
    OCEANIA = "Oceania"
    ASIA = "Asia"


def validate_password(v: str) -> str:
    digit = False
    upper_alpha = False
    lower_alpha = False
    for symbol in v:
        if symbol.isdigit():
            digit = True
        if symbol.isalpha() and symbol.isupper():
            upper_alpha = True
        if symbol.isalpha() and symbol.islower():
            lower_alpha = True
    if not (digit and upper_alpha and lower_alpha):
        msg = "Password does not meet the requirements"
        raise ValueError(msg)
    return v


class RegisterUser(BaseModel):
    login: Annotated[str, Field(max_length=30, pattern=r"[a-zA-Z0-9-]+")]
    email: Annotated[EmailStr, Field(min_length=1, max_length=50)]
    password: Annotated[str, Field(min_length=6, max_length=100), AfterValidator(validate_password)]
    country_code: Annotated[str, Field(alias="countryCode", max_length=2, pattern=r"[a-zA-Z]{2}")]
    is_public: Annotated[bool, Field(alias="isPublic")]
    phone: Annotated[str | None, Field(max_length=20, pattern=r"\+[\d]+")] = None
    image: Annotated[str | None, Field(min_length=1, max_length=200)] = None


class SignInUser(BaseModel):
    login: Annotated[str, Field(max_length=30, pattern=r"[a-zA-Z0-9-]+")]
    password: Annotated[str, Field(min_length=6, max_length=100), AfterValidator(validate_password)]


class UpdateUser(pydantic.BaseModel):
    country_code: Annotated[
        str | None,
        Field(alias="countryCode", max_length=2, pattern=r"[a-zA-Z]{2}"),
    ] = None
    is_public: Annotated[bool | None, Field(alias="isPublic")] = None
    phone: Annotated[str | None, Field(max_length=20, pattern=r"\+[\d]+")] = None
    image: Annotated[str | None, Field(min_length=1, max_length=200)] = None


class UpdatePassword(BaseModel):
    oldPassword: Annotated[str, Field(min_length=6, max_length=100), AfterValidator(validate_password)]
    newPassword: Annotated[str, Field(min_length=6, max_length=100), AfterValidator(validate_password)]


class AddFriend(BaseModel):
    login: Annotated[str, Field(max_length=30, pattern=r"[a-zA-Z0-9-]+")]


class CreatePost(BaseModel):
    content: Annotated[str, Field(max_length=1000)]
    tags: list[str]

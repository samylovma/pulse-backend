import enum
from typing import Annotated

import pydantic
from pydantic import AfterValidator, EmailStr, Field


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
    login: Annotated[str, Field(max_length=30, pattern=r"[a-zA-Z0-9-]+")]
    email: Annotated[EmailStr, Field(min_length=1, max_length=50)]
    countryCode: Annotated[str, Field(max_length=2, pattern=r"[a-zA-Z]{2}")]
    isPublic: bool
    phone: Annotated[str | None, Field(max_length=20, pattern=r"\+[\d]+")] = (
        None
    )
    image: Annotated[str | None, Field(min_length=1, max_length=200)] = None


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
        raise ValueError("Password does not meet the requirements")
    return v


class RegisterUser(UserProfile):
    password: Annotated[
        str,
        Field(min_length=6, max_length=100),
        AfterValidator(validate_password),
    ]


class SignInUser(BaseModel):
    login: Annotated[str, Field(max_length=30, pattern=r"[a-zA-Z0-9-]+")]
    password: Annotated[
        str,
        Field(min_length=6, max_length=100),
        AfterValidator(validate_password),
    ]


class UpdateUser(pydantic.BaseModel):
    countryCode: Annotated[
        str | None, Field(max_length=2, pattern=r"[a-zA-Z]{2}")
    ] = None
    isPublic: bool | None = None
    phone: Annotated[str | None, Field(max_length=20, pattern=r"\+[\d]+")] = (
        None
    )
    image: Annotated[str | None, Field(min_length=1, max_length=200)] = None


class UpdatePassword(BaseModel):
    oldPassword: Annotated[
        str,
        Field(min_length=6, max_length=100),
        AfterValidator(validate_password),
    ]
    newPassword: Annotated[
        str,
        Field(min_length=6, max_length=100),
        AfterValidator(validate_password),
    ]


class AddFriend(BaseModel):
    login: Annotated[str, Field(max_length=30, pattern=r"[a-zA-Z0-9-]+")]

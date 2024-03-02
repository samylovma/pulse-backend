from typing import Annotated

import pydantic


class UserProfile(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    login: str
    email: str
    country_code: Annotated[
        str, pydantic.Field(serialization_alias="countryCode")
    ]
    is_public: Annotated[bool, pydantic.Field(serialization_alias="isPublic")]
    phone: str | None
    image: str | None

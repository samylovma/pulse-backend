from typing import Any

from litestar import Controller, Request, get
from litestar.security.jwt import Token

from pulse_backend.db_schema import User
from pulse_backend.schemas import UserProfile


class MeController(Controller):
    path = "/me"

    @get("/profile")
    async def profile(
        self, request: Request[User, Token, Any]
    ) -> dict[str, Any]:
        return UserProfile.model_validate(request.user).model_dump(
            by_alias=True, exclude_none=True
        )

from typing import Annotated, Any

from litestar import get, Request
from litestar.params import Parameter
from litestar.exceptions import PermissionDeniedException
from litestar.security import jwt

from pulse_backend.schema import UserProfile
from pulse_backend.deps import provide_user_service, provide_friend_service
from pulse_backend.services import UserService, FriendService
from pulse_backend.db_schema import User, Friend


@get(
    "/api/profiles/{login:str}",
    dependencies={
        "user_service": provide_user_service,
        "friend_service": provide_friend_service,
    },
)
async def get_profile(
    request: Request[User, jwt.Token, Any],
    login: Annotated[
        str,
        Parameter(
            max_length=30,
            pattern=r"[a-zA-Z0-9-]+",
        ),
    ],
    user_service: UserService,
    friend_service: FriendService,
) -> dict[str, Any]:
    user: User | None = await user_service.get_one_or_none(login=login)
    if user is None:
        raise PermissionDeniedException("User does not exist")

    friend: Friend | None = await friend_service.get_one_or_none(
        of_login=request.user.login, login=user.login
    )

    if user.isPublic is False and user != request.user and friend is None:
        raise PermissionDeniedException("No access to user profile")

    return UserProfile.model_validate(user).model_dump(exclude_none=True)

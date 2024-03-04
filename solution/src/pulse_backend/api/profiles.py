from typing import Annotated, Any

from litestar import Request, get
from litestar.exceptions import PermissionDeniedException
from litestar.params import Parameter
from litestar.security import jwt

from pulse_backend.db_schema import Friend, User
from pulse_backend.deps import provide_friend_service, provide_user_service
from pulse_backend.schema import UserProfile
from pulse_backend.services import FriendService, UserService


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
        of_login=user.login, login=request.user.login
    )

    f = False
    if user.isPublic is True:
        f = True
    if user.isPublic is False:
        if user.login == request.user.login:
            f = True
        if isinstance(friend, Friend):
            f = True

    if f is False:
        raise PermissionDeniedException("No access to user profile")

    return UserProfile.model_validate(user).model_dump(exclude_none=True)

from typing import Annotated, Any

from litestar import Request, get
from litestar.exceptions import PermissionDeniedException
from litestar.params import Parameter
from litestar.security import jwt

from pulse_backend.db_models import Friend, User
from pulse_backend.dependencies import (
    provide_friend_service,
    provide_user_service,
)
from pulse_backend.dto import UserDTO
from pulse_backend.services import FriendService, UserService


@get(
    "/api/profiles/{login:str}",
    dependencies={"user_service": provide_user_service, "friend_service": provide_friend_service},
    return_dto=UserDTO,
)
async def get_profile(
    request: Request[User, jwt.Token, Any],
    login: Annotated[str, Parameter(max_length=30, pattern=r"[a-zA-Z0-9-]+")],
    user_service: UserService,
    friend_service: FriendService,
) -> User:
    user = await user_service.get_one_or_none(login=login)
    if user is None:
        raise PermissionDeniedException("User does not exist")

    friend: Friend | None = await friend_service.get_one_or_none(of_login=user.login, login=request.user.login)

    f = False
    if user.is_public is True:
        f = True
    if user.is_public is False:
        if user.login == request.user.login:
            f = True
        if isinstance(friend, Friend):
            f = True

    if f is False:
        raise PermissionDeniedException("No access to user profile")

    return user

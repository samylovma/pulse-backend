from datetime import UTC, datetime
from typing import Annotated, Any, Self

import sqlalchemy as sa
from advanced_alchemy.filters import LimitOffset, OrderBy
from litestar import Controller, Request, get, post
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from litestar.params import Parameter
from litestar.status_codes import HTTP_200_OK

from pulse_backend.db_models import Friend, Session, User
from pulse_backend.dependencies import (
    provide_friend_service,
    provide_user_service,
)
from pulse_backend.schemas import AddFriend
from pulse_backend.services import FriendService, UserService


class FriendsController(Controller):
    dependencies = {  # noqa: RUF012
        "user_service": Provide(provide_user_service),
        "friend_service": Provide(provide_friend_service),
    }

    @post("/api/friends/add", status_code=HTTP_200_OK)
    async def add_friend(
        self: Self,
        data: AddFriend,
        request: Request[User, Session, Any],
        user_service: UserService,
        friend_service: FriendService,
    ) -> dict[str, Any]:
        friend_user: User | None = await user_service.get_one_or_none(login=data.login)
        if friend_user is None:
            raise NotFoundException("User not found")
        if friend_user.login == request.user.login:
            return {"status": "ok"}

        friend = Friend(
            of_login=request.user.login,
            login=friend_user.login,
            addedAt=datetime.now(UTC),
        )
        await friend_service.upsert(friend, match_fields=["of_login", "login"])

        return {"status": "ok"}

    @post("/api/friends/remove", status_code=HTTP_200_OK)
    async def remove_friend(
        self: Self,
        data: AddFriend,
        request: Request[User, Session, Any],
        friend_service: FriendService,
    ) -> dict[str, Any]:
        stmt = sa.delete(Friend).where(Friend.of_login == request.user.login).where(Friend.login == data.login)
        await friend_service.repository.session.execute(stmt)
        await friend_service.repository.session.commit()
        return {"status": "ok"}

    @get("/api/friends")
    async def list_friends(
        self: Self,
        request: Request[User, Session, Any],
        friend_service: FriendService,
        limit: Annotated[int, Parameter(ge=0, le=50)] = 5,
        offset: Annotated[int, Parameter(ge=0)] = 0,
    ) -> list[dict[str, Any]]:
        friends = await friend_service.list(
            OrderBy(field_name="addedAt", sort_order="desc"),
            LimitOffset(limit=limit, offset=offset),
            of_login=request.user.login,
        )
        return [{"login": friend.login, "addedAt": friend.addedAt.isoformat()} for friend in friends]

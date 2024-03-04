from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Annotated, Any

from advanced_alchemy.filters import LimitOffset, OrderBy
from litestar import Controller, Request, get, post
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from litestar.pagination import AbstractAsyncOffsetPaginator, OffsetPagination
from litestar.params import Parameter
from litestar.security import jwt
from litestar.status_codes import HTTP_200_OK
from sqlalchemy import delete, update

from pulse_backend.db_schema import Friend, User
from pulse_backend.deps import provide_friend_service, provide_user_service
from pulse_backend.schema import AddFriend
from pulse_backend.services import FriendService, UserService


class FriendsOffsetPaginator(AbstractAsyncOffsetPaginator[Friend]):
    def __init__(self, friend_service: FriendService) -> None:
        self.friend_service = friend_service

    async def __call__(  # type: ignore[override]
        self, limit: int, offset: int, of_login: str
    ) -> OffsetPagination[Friend]:
        self.of_login = of_login
        return await super().__call__(limit=limit, offset=offset)

    async def get_total(self) -> int:
        return await self.friend_service.count()

    async def get_items(self, limit: int, offset: int) -> list[Friend]:
        friends: Sequence[Friend] = await self.friend_service.list(
            OrderBy(field_name="addedAt", sort_order="desc"),
            LimitOffset(limit=limit, offset=offset),
            of_login=self.of_login,
        )
        return list(friends)


class FriendsController(Controller):
    dependencies = {
        "user_service": Provide(provide_user_service),
        "friend_service": Provide(provide_friend_service),
    }

    @post("/api/friends/add", status_code=HTTP_200_OK)
    async def add_friend(
        self,
        data: AddFriend,
        request: Request[User, jwt.Token, Any],
        user_service: UserService,
        friend_service: FriendService,
    ) -> dict[str, Any]:
        friend_user: User | None = await user_service.get_one_or_none(
            login=data.login
        )
        if friend_user is None:
            raise NotFoundException("User not found")
        if friend_user.login == request.user.login:
            return {"status": "ok"}

        friend = await friend_service.get_one_or_none(
            of_login=request.user.login, login=friend_user.login
        )
        if friend is None:
            friend = Friend(
                of_login=request.user.login,
                login=friend_user.login,
                addedAt=datetime.now(UTC),
            )
            await friend_service.create(friend, auto_commit=True)
        else:
            stmt = (
                update(Friend)
                .where(
                    Friend.of_login == request.user.login
                    and Friend.login == friend_user.login
                )
                .values(addedAt=datetime.now(UTC))
            )
            await friend_service.repository.session.execute(stmt)
            await friend_service.repository.session.commit()

        return {"status": "ok"}

    @post("/api/friends/remove")
    async def remove_friend(
        self,
        data: AddFriend,
        request: Request[User, jwt.Token, Any],
        user_service: UserService,
        friend_service: FriendService,
    ) -> dict[str, Any]:
        friend: Friend | None = await friend_service.get_one_or_none(
            of_login=request.user.login, login=data.login
        )
        if friend is None:
            return {"status": "ok"}

        stmt = (
            delete(Friend)
            .where(Friend.of_login == request.user.login)
            .where(Friend.login == data.login)
        )
        await friend_service.repository.session.execute(stmt)
        await friend_service.repository.session.commit()

        return {"status": "ok"}

    @get(
        "/api/friends",
        dependencies={"paginator": Provide(FriendsOffsetPaginator)},
    )
    async def list_friends(
        self,
        request: Request[User, jwt.Token, Any],
        paginator: FriendsOffsetPaginator,
        limit: Annotated[int, Parameter(ge=0, le=50)] = 5,
        offset: Annotated[int, Parameter(ge=0)] = 0,
    ) -> list[dict[str, Any]]:
        result = await paginator(
            limit=limit, offset=offset, of_login=request.user.login
        )
        return [
            {"login": item.login, "addedAt": item.addedAt.isoformat()}
            for item in result.items
        ]

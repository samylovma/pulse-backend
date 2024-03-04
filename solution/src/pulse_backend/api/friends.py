from typing import Any
from datetime import datetime, UTC

from litestar import Controller, post, Request
from litestar.status_codes import HTTP_200_OK
from litestar.security import jwt
from litestar.exceptions import NotFoundException
from sqlalchemy import update, delete

from pulse_backend.deps import provide_user_service, provide_friend_service
from pulse_backend.schema import AddFriend
from pulse_backend.services import UserService, FriendService
from pulse_backend.db_schema import User, Friend


class FriendsController(Controller):
    dependencies = {
        "user_service": provide_user_service,
        "friend_service": provide_friend_service,
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

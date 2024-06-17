from datetime import UTC, datetime
from typing import Annotated, Any, Self
from uuid import UUID, uuid4

from advanced_alchemy.filters import LimitOffset, OrderBy
from litestar import Controller, Request, get, post
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from litestar.params import Parameter
from litestar.status_codes import HTTP_200_OK

from pulse_backend.db_models import Friend, Post, Session, User
from pulse_backend.dependencies import (
    provide_friend_service,
    provide_post_service,
    provide_user_service,
)
from pulse_backend.schemas import CreatePost
from pulse_backend.services import FriendService, PostService, UserService


class PostsController(Controller):
    dependencies = {  # noqa: RUF012
        "post_service": Provide(provide_post_service),
        "friend_service": Provide(provide_friend_service),
        "user_service": Provide(provide_user_service),
    }

    @post("/api/posts/new", status_code=HTTP_200_OK)
    async def create_post(
        self: Self,
        data: CreatePost,
        request: Request[User, Session, Any],
        post_service: PostService,
    ) -> dict[str, Any]:
        post_ = Post(
            id=uuid4(),
            content=data.content,
            author=request.user.login,
            tags=data.tags,
            createdAt=datetime.now(UTC),
        )
        post_ = await post_service.create(post_)
        return {
            "id": post_.id,
            "content": post_.content,
            "author": post_.author,
            "tags": post_.tags,
            "createdAt": post_.createdAt.isoformat(),
            "likesCount": post_.likesCount,
            "dislikesCount": post_.dislikesCount,
        }

    @get("/api/posts/{postId:uuid}")
    async def get_post(
        self: Self,
        post_id: Annotated[UUID, Parameter(query="postId")],
        request: Request[User, Session, Any],
        post_service: PostService,
        friend_service: FriendService,
    ) -> dict[str, Any]:
        post_ = await post_service.get_one_or_none(id=post_id)
        if post_ is None:
            raise NotFoundException("Post not found")

        friend: Friend | None = await friend_service.get_one_or_none(of_login=post_.author, login=request.user.login)

        f = False
        if post_.user.is_public is True:
            f = True
        if post_.user.is_public is False:
            if request.user.login == post_.author:
                f = True
            if isinstance(friend, Friend):
                f = True

        if f is False:
            raise NotFoundException("No access to post")

        return {
            "id": post_.id,
            "content": post_.content,
            "author": post_.author,
            "tags": post_.tags,
            "createdAt": post_.createdAt.isoformat(),
            "likesCount": post_.likesCount,
            "dislikesCount": post_.dislikesCount,
        }

    @get("/api/posts/feed/my")
    async def feed_my(
        self: Self,
        request: Request[User, Session, Any],
        post_service: PostService,
        limit: Annotated[int, Parameter(ge=0, le=50)] = 5,
        offset: Annotated[int, Parameter(ge=0)] = 0,
    ) -> list[dict[str, Any]]:
        posts = await post_service.list(
            OrderBy(field_name="createdAt", sort_order="desc"),
            LimitOffset(limit=limit, offset=offset),
            author=request.user.login,
        )
        return [
            {
                "id": post_.id,
                "content": post_.content,
                "author": post_.author,
                "tags": post_.tags,
                "createdAt": post_.createdAt.isoformat(),
                "likesCount": post_.likesCount,
                "dislikesCount": post_.dislikesCount,
            }
            for post_ in posts
        ]

    @get("/api/posts/feed/{login:str}")
    async def feed_user(  # noqa: PLR0913
        self: Self,
        login: Annotated[
            str,
            Parameter(
                max_length=30,
                pattern=r"[a-zA-Z0-9-]+",
            ),
        ],
        request: Request[User, Session, Any],
        user_service: UserService,
        friend_service: FriendService,
        post_service: PostService,
        limit: Annotated[int, Parameter(ge=0, le=50)] = 5,
        offset: Annotated[int, Parameter(ge=0)] = 0,
    ) -> list[dict[str, Any]]:
        user = await user_service.get_one_or_none(login=login)
        if user is None:
            raise NotFoundException("User not found")

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
            raise NotFoundException("No access to user's posts")

        posts = await post_service.list(
            OrderBy(field_name="createdAt", sort_order="desc"),
            LimitOffset(limit=limit, offset=offset),
            author=login,
        )
        return [
            {
                "id": post_.id,
                "content": post_.content,
                "author": post_.author,
                "tags": post_.tags,
                "createdAt": post_.createdAt.isoformat(),
                "likesCount": post_.likesCount,
                "dislikesCount": post_.dislikesCount,
            }
            for post_ in posts
        ]

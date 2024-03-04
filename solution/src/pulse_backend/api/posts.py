from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Annotated, Any
from uuid import UUID, uuid4

from advanced_alchemy.exceptions import NotFoundError
from advanced_alchemy.filters import LimitOffset, OrderBy
from litestar import Controller, Request, get, post
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from litestar.pagination import AbstractAsyncOffsetPaginator, OffsetPagination
from litestar.params import Parameter
from litestar.security import jwt
from litestar.status_codes import HTTP_200_OK

from pulse_backend.db_schema import Friend, Post, User
from pulse_backend.deps import (
    provide_friend_service,
    provide_post_service,
    provide_user_service,
)
from pulse_backend.schema import CreatePost
from pulse_backend.services import FriendService, PostService, UserService


class PostsOffsetPaginator(AbstractAsyncOffsetPaginator[Post]):
    def __init__(self, post_service: PostService) -> None:
        self.post_service = post_service

    async def __call__(  # type: ignore[override]
        self, limit: int, offset: int, author: str
    ) -> OffsetPagination[Post]:
        self.author = author
        return await super().__call__(limit=limit, offset=offset)

    async def get_total(self) -> int:
        return await self.post_service.count()

    async def get_items(self, limit: int, offset: int) -> list[Post]:
        posts: Sequence[Post] = await self.post_service.list(
            OrderBy(field_name="createdAt", sort_order="desc"),
            LimitOffset(limit=limit, offset=offset),
            author=self.author,
        )
        return list(posts)


class PostsController(Controller):
    dependencies = {
        "post_service": Provide(provide_post_service),
        "friend_service": Provide(provide_friend_service),
        "user_service": Provide(provide_user_service),
    }

    @post("/api/posts/new", status_code=HTTP_200_OK)
    async def create_post(
        self,
        data: CreatePost,
        request: Request[User, jwt.Token, Any],
        post_service: PostService,
    ) -> dict[str, Any]:
        post_ = Post(
            id=uuid4(),
            content=data.content,
            author=request.user.login,
            tags=data.tags,
            createdAt=datetime.now(UTC),
        )
        post_ = await post_service.create(post_, auto_commit=True)
        return {
            "id": post_.id,
            "content": post_.content,
            "author": post_.author,
            "tags": post_.tags,
            "createdAt": post_.createdAt.isoformat(),
            "likesCount": post_.likesCount,
            "dislikesCount": post_.dislikesCount,
        }

    @get("/api/posts/{postId:str}")
    async def get_post(
        self,
        postId: UUID,
        request: Request[User, jwt.Token, Any],
        post_service: PostService,
        friend_service: FriendService,
    ) -> dict[str, Any]:
        try:
            post_: Post = await post_service.get(postId)
        except NotFoundError as e:
            raise NotFoundException("Post not found") from e

        friend: Friend | None = await friend_service.get_one_or_none(
            of_login=post_.author, login=request.user.login
        )

        f = False
        if post_.user.isPublic is True:
            f = True
        if post_.user.isPublic is False:
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

    @get(
        "/api/posts/feed/my",
        dependencies={"paginator": Provide(PostsOffsetPaginator)},
    )
    async def feed_my(
        self,
        request: Request[User, jwt.Token, Any],
        paginator: PostsOffsetPaginator,
        limit: Annotated[int, Parameter(ge=0, le=50)] = 5,
        offset: Annotated[int, Parameter(ge=0)] = 0,
    ) -> list[dict[str, Any]]:
        result = await paginator(
            limit=limit, offset=offset, author=request.user.login
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
            for post_ in result.items
        ]

    @get(
        "/api/posts/feed/{login:str}",
        dependencies={"paginator": Provide(PostsOffsetPaginator)},
    )
    async def feed_user(
        self,
        login: Annotated[
            str,
            Parameter(
                max_length=30,
                pattern=r"[a-zA-Z0-9-]+",
            ),
        ],
        request: Request[User, jwt.Token, Any],
        user_service: UserService,
        friend_service: FriendService,
        paginator: PostsOffsetPaginator,
        limit: Annotated[int, Parameter(ge=0, le=50)] = 5,
        offset: Annotated[int, Parameter(ge=0)] = 0,
    ) -> list[dict[str, Any]]:
        user: User | None = await user_service.get_one_or_none(login=login)
        if user is None:
            raise NotFoundException("User not found")

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
            raise NotFoundException("No access to user's posts")

        result = await paginator(limit=limit, offset=offset, author=login)
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
            for post_ in result.items
        ]

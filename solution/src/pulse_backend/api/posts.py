from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from advanced_alchemy.exceptions import NotFoundError
from litestar import Controller, Request, get, post
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from litestar.security import jwt

from pulse_backend.db_schema import Friend, Post, User
from pulse_backend.deps import provide_friend_service, provide_post_service
from pulse_backend.schema import CreatePost
from pulse_backend.services import FriendService, PostService


class PostsController(Controller):
    dependencies = {
        "post_service": Provide(provide_post_service),
        "friend_service": Provide(provide_friend_service),
    }

    @post("/api/posts/new")
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

        if f is True:
            return {
                "id": post_.id,
                "content": post_.content,
                "author": post_.author,
                "tags": post_.tags,
                "createdAt": post_.createdAt.isoformat(),
                "likesCount": post_.likesCount,
                "dislikesCount": post_.dislikesCount,
            }

        raise NotFoundException("No access to post")

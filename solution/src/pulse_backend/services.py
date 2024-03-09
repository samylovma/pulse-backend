from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from pulse_backend.db.models import Country, Friend, Post, Session, User
from pulse_backend.repositories import (
    CountryRepository,
    FriendRepository,
    PostRepository,
    SessionRepository,
    UserRepository,
)


class CountryService(SQLAlchemyAsyncRepositoryService[Country]):
    repository_type = CountryRepository


class UserService(SQLAlchemyAsyncRepositoryService[User]):
    repository_type = UserRepository


class FriendService(SQLAlchemyAsyncRepositoryService[Friend]):
    repository_type = FriendRepository


class PostService(SQLAlchemyAsyncRepositoryService[Post]):
    repository_type = PostRepository


class SessionService(SQLAlchemyAsyncRepositoryService[Session]):
    repository_type = SessionRepository

from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository

from pulse_backend.db.models import Country, Friend, Post, Session, User


class CountryRepository(SQLAlchemyAsyncRepository[Country]):
    model_type = Country


class UserRepository(SQLAlchemyAsyncRepository[User]):
    model_type = User


class FriendRepository(SQLAlchemyAsyncRepository[Friend]):
    model_type = Friend


class PostRepository(SQLAlchemyAsyncRepository[Post]):
    model_type = Post


class SessionRepository(SQLAlchemyAsyncRepository[Session]):
    model_type = Session

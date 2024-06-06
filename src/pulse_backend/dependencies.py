from sqlalchemy.ext.asyncio import AsyncSession

from pulse_backend.services import (
    CountryService,
    FriendService,
    PostService,
    SessionService,
    UserService,
)


async def provide_country_service(db_session: AsyncSession) -> CountryService:
    return CountryService(session=db_session, auto_commit=True)


async def provide_user_service(db_session: AsyncSession) -> UserService:
    return UserService(session=db_session, auto_commit=True)


async def provide_friend_service(db_session: AsyncSession) -> FriendService:
    return FriendService(session=db_session, auto_commit=True)


async def provide_post_service(db_session: AsyncSession) -> PostService:
    return PostService(session=db_session, auto_commit=True)


async def provide_session_service(db_session: AsyncSession) -> SessionService:
    return SessionService(session=db_session, auto_commit=True)

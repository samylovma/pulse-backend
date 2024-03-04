from sqlalchemy.ext.asyncio import AsyncSession

from pulse_backend.services import (
    UserService,
    CountryService,
    TokenService,
    FriendService,
)
from pulse_backend.jwt import jwt_auth


async def provide_country_service(db_session: AsyncSession) -> CountryService:
    return CountryService(session=db_session)


async def provide_user_service(db_session: AsyncSession) -> UserService:
    return UserService(session=db_session)


async def provide_friend_service(db_session: AsyncSession) -> FriendService:
    return FriendService(session=db_session)


async def provide_token_service(db_session: AsyncSession) -> TokenService:
    return TokenService(db_session, jwt_auth)

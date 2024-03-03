from sqlalchemy.ext.asyncio import AsyncSession

from pulse_backend.services import UserService, CountryService


async def provide_country_service(db_session: AsyncSession) -> CountryService:
    return CountryService(session=db_session)


async def provide_user_service(db_session: AsyncSession) -> UserService:
    return UserService(session=db_session)

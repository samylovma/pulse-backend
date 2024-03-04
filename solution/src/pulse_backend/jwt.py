from os import getenv
from typing import Any

from litestar.connection import ASGIConnection
from litestar.security.jwt import JWTAuth
from litestar.security.jwt import Token as JWTToken

from pulse_backend.db_schema import Token, User
from pulse_backend.services import TokenService


async def retrieve_user_handler(
    token: JWTToken, connection: ASGIConnection[Any, Any, Any, Any]
) -> User | None:
    db_session = await connection.app.dependencies["db_session"](
        state=connection.app.state, scope=connection.scope
    )
    token_service = TokenService(db_session, jwt_auth)
    token_model: Token | None = await token_service.get(token)
    if isinstance(token_model, Token):
        return token_model.user
    return None


jwt_auth = JWTAuth[User](
    retrieve_user_handler=retrieve_user_handler,
    token_secret=getenv("RANDOM_SECRET", "token"),
    exclude=[
        "/api/ping",
        "/api/countries",
        "/api/auth/register",
        "/api/auth/sign-in",
    ],
)

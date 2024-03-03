from os import getenv
from typing import Any

from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.security.jwt import JWTAuth, Token

from pulse_backend.services import TokenService
from pulse_backend import db_schema


async def retrieve_user_handler(
    token: Token, connection: ASGIConnection[Any, Any, Any, Any]
) -> db_schema.User | None:
    db_session = await connection.app.dependencies["db_session"](
        state=connection.app.state, scope=connection.scope
    )
    token_service = TokenService(db_session, jwt_auth)
    token_model = await token_service.get(
        token.encode(
            secret=jwt_auth.token_secret, algorithm=jwt_auth.algorithm
        )
    )
    if token_model is None or token_model.is_revoked:
        raise NotAuthorizedException()
    return token_model.user


jwt_auth = JWTAuth[db_schema.User](
    retrieve_user_handler=retrieve_user_handler,
    token_secret=getenv("RANDOM_SECRET", "token"),
    exclude=[
        "/api/ping",
        "/api/countries",
        "/api/auth/register",
        "/api/auth/sign-in",
    ],
)

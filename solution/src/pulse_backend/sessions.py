from collections.abc import Sequence
from dataclasses import dataclass
from os import getenv
from typing import Any

from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWTError
from litestar.config.app import AppConfig
from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.middleware import DefineMiddleware
from litestar.middleware.authentication import (
    AbstractAuthenticationMiddleware,
    AuthenticationResult,
)
from litestar.types import ASGIApp, Method, Scopes

from pulse_backend.db_models import Session
from pulse_backend.dependencies import provide_session_service


# pylint: disable=too-few-public-methods,too-many-arguments
class JWTSessionAuthenticationMiddleware(AbstractAuthenticationMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        exclude: str | list[str],
        exclude_from_auth_key: str,
        exclude_http_methods: Sequence[Method],
        scopes: Scopes,
        token_secret: str,
    ) -> None:
        super().__init__(
            app=app,
            exclude=exclude,
            exclude_from_auth_key=exclude_from_auth_key,
            exclude_http_methods=exclude_http_methods,
            scopes=scopes,
        )
        self.token_secret = token_secret

    async def authenticate_request(
        self, connection: ASGIConnection[Any, Any, Any, Any]
    ) -> AuthenticationResult:
        auth_header = connection.headers.get("Authorization")
        if auth_header is None:
            raise NotAuthorizedException('No "Authorization" header')
        if auth_header[:6] != "Bearer":
            raise NotAuthorizedException(
                "The authentication scheme is not supported"
            )

        try:
            claims = jwt.decode(
                token=auth_header[7:],
                key=self.token_secret,
                algorithms="HS256",
                options={"require_jti": True, "require_exp": True},
            )
        except (JWTError, ExpiredSignatureError, JWTClaimsError) as e:
            raise NotAuthorizedException("Invalid token") from e

        db_session = await connection.app.dependencies["db_session"](
            state=connection.app.state, scope=connection.scope
        )
        session_service = await provide_session_service(db_session)
        session = await session_service.get_one_or_none(id=claims["jti"])
        if session is None:
            raise NotAuthorizedException("Invalid token")

        return AuthenticationResult(user=session.user, auth=session)


@dataclass(slots=True)
class JWTSessionAuthentication:
    token_secret: str
    exclude: str | list[str] | None = None
    exclude_from_auth_key: str = "exclude_from_auth"
    exclude_http_methods: Sequence[Method] | None = ("OPTIONS", "HEAD")
    scopes: "Scopes | None" = None

    @property
    def middleware(self) -> DefineMiddleware:
        return DefineMiddleware(
            JWTSessionAuthenticationMiddleware,
            exclude=self.exclude,
            exclude_from_auth_key=self.exclude_from_auth_key,
            exclude_http_methods=self.exclude_http_methods,
            scopes=self.scopes,
            token_secret=self.token_secret,
        )

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        app_config.middleware.insert(0, self.middleware)
        return app_config

    def create_token(self, session: Session) -> str:
        return jwt.encode(
            claims={
                "jti": str(session.id),
                "exp": session.exp.timestamp(),
            },
            key=self.token_secret,
        )


auth = JWTSessionAuthentication(
    token_secret=getenv("RANDOM_SECRET", "token"),
    exclude=[
        "/schema",
        "/api/ping",
        "/api/countries",
        "/api/auth/register",
        "/api/auth/sign-in",
    ],
)

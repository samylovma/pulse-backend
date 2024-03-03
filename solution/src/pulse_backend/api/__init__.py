from litestar import Router

from pulse_backend.api.auth import AuthController
from pulse_backend.api.country import CountryController
from pulse_backend.api.me import MeController
from pulse_backend.api.ping import ping


def create_router() -> Router:
    return Router(
        "/",
        route_handlers=(ping, CountryController, AuthController, MeController),
    )

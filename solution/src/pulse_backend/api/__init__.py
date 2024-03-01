from litestar import Router

from pulse_backend.api.country import CountryController
from pulse_backend.api.ping import ping


def create_router() -> Router:
    return Router("/api", route_handlers=(ping, CountryController))

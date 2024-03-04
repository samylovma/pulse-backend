from litestar import Router

from .auth import AuthController
from .country import CountryController
from .me import MeController
from .ping import ping
from .profiles import get_profile
from .friends import FriendsController


def create_router() -> Router:
    return Router(
        "/",
        route_handlers=(
            ping,
            CountryController,
            AuthController,
            MeController,
            get_profile,
            FriendsController,
        ),
    )

from litestar import Router

from .auth import AuthController
from .country import CountryController
from .friends import FriendsController
from .me import MeController
from .ping import ping
from .posts import PostsController
from .profiles import get_profile


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
            PostsController,
        ),
    )

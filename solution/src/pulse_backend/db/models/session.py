from typing import TYPE_CHECKING

from advanced_alchemy.base import UUIDBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .user import User


class Session(UUIDBase):  # pylint: disable=too-few-public-methods
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(lazy="joined")

# pylint: disable=unsubscriptable-object,too-few-public-methods

from datetime import datetime
from typing import TYPE_CHECKING

from advanced_alchemy.base import UUIDBase
from sqlalchemy import TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .user import User


class Session(UUIDBase):
    exp: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(lazy="joined")

from datetime import datetime
from typing import TYPE_CHECKING

from advanced_alchemy.base import (
    UUIDBase,
)
from sqlalchemy import TIMESTAMP, ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .user import User


class Post(UUIDBase):  # pylint: disable=too-few-public-methods
    content: Mapped[str] = mapped_column(String(1000))
    author: Mapped[str] = mapped_column(ForeignKey("user.login"))
    tags: Mapped[list[str]] = mapped_column(ARRAY(String(20)))
    createdAt: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    likesCount: Mapped[int] = mapped_column(default=0)
    dislikesCount: Mapped[int] = mapped_column(default=0)

    user: Mapped["User"] = relationship(lazy="joined")

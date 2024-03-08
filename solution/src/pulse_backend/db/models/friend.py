from datetime import datetime

from advanced_alchemy.base import BigIntBase
from sqlalchemy import TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class Friend(BigIntBase):  # pylint: disable=too-few-public-methods
    of_login: Mapped[str] = mapped_column(
        ForeignKey("user.login"), primary_key=True
    )
    login: Mapped[str] = mapped_column(
        ForeignKey("user.login"), primary_key=True
    )
    addedAt: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))

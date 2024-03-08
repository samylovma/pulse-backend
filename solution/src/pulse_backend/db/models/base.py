from advanced_alchemy.base import CommonTableAttributes, orm_registry
from sqlalchemy.orm import DeclarativeBase


# pylint: disable=too-few-public-methods
class Base(CommonTableAttributes, DeclarativeBase):
    registry = orm_registry

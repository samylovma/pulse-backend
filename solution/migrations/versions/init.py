# type: ignore
"""init

Revision ID: b26271a94417
Revises:
Create Date: 2024-03-10 14:22:55.196280+00:00

"""

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

import sqlalchemy as sa
from advanced_alchemy.types import (
    GUID,
    ORA_JSONB,
    DateTimeUTC,
    EncryptedString,
    EncryptedText,
)
from alembic import op
from sqlalchemy import Text  # noqa: F401

if TYPE_CHECKING:
    pass

__all__ = [
    "downgrade",
    "upgrade",
    "schema_upgrades",
    "schema_downgrades",
    "data_upgrades",
    "data_downgrades",
]

sa.GUID = GUID
sa.DateTimeUTC = DateTimeUTC
sa.ORA_JSONB = ORA_JSONB
sa.EncryptedString = EncryptedString
sa.EncryptedText = EncryptedText

# revision identifiers, used by Alembic.
revision = "b26271a94417"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        with op.get_context().autocommit_block():
            schema_upgrades()
            data_upgrades()


def downgrade() -> None:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        with op.get_context().autocommit_block():
            data_downgrades()
            schema_downgrades()


def schema_upgrades() -> None:
    """schema upgrade migrations go here."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user",
        sa.Column("login", sa.String(length=30), nullable=False),
        sa.Column("email", sa.String(length=50), nullable=False),
        sa.Column("hashed_password", sa.LargeBinary(), nullable=False),
        sa.Column("countryCode", sa.String(length=2), nullable=False),
        sa.Column("isPublic", sa.Boolean(), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("image", sa.String(length=200), nullable=True),
        sa.PrimaryKeyConstraint("login", name=op.f("pk_user")),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("email", name=op.f("uq_user_email")),
        sa.UniqueConstraint("login"),
        sa.UniqueConstraint("login", name=op.f("uq_user_login")),
        sa.UniqueConstraint("phone"),
        sa.UniqueConstraint("phone", name=op.f("uq_user_phone")),
    )
    op.create_table(
        "friend",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            nullable=False,
        ),
        sa.Column("of_login", sa.String(length=30), nullable=False),
        sa.Column("login", sa.String(length=30), nullable=False),
        sa.Column("addedAt", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["login"], ["user.login"], name=op.f("fk_friend_login_user")
        ),
        sa.ForeignKeyConstraint(
            ["of_login"], ["user.login"], name=op.f("fk_friend_of_login_user")
        ),
        sa.PrimaryKeyConstraint(
            "of_login", "login", "id", name=op.f("pk_friend")
        ),
    )
    op.create_table(
        "post",
        sa.Column("id", sa.GUID(length=16), nullable=False),
        sa.Column("content", sa.String(length=1000), nullable=False),
        sa.Column("author", sa.String(length=30), nullable=False),
        sa.Column("tags", sa.ARRAY(sa.String(length=20)), nullable=False),
        sa.Column("createdAt", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("likesCount", sa.Integer(), nullable=False),
        sa.Column("dislikesCount", sa.Integer(), nullable=False),
        sa.Column("sa_orm_sentinel", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["author"], ["user.login"], name=op.f("fk_post_author_user")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_post")),
    )
    op.create_table(
        "session",
        sa.Column("id", sa.GUID(length=16), nullable=False),
        sa.Column("exp", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("user_login", sa.String(length=30), nullable=False),
        sa.Column("sa_orm_sentinel", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_login"],
            ["user.login"],
            name=op.f("fk_session_user_login_user"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_session")),
    )
    # ### end Alembic commands ###


def schema_downgrades() -> None:
    """schema downgrade migrations go here."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("session")
    op.drop_table("post")
    op.drop_table("friend")
    op.drop_table("user")
    # ### end Alembic commands ###


def data_upgrades() -> None:
    """Add any optional data upgrade migrations here!"""


def data_downgrades() -> None:
    """Add any optional data downgrade migrations here!"""

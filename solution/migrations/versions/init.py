"""init

Revision ID: c744e4868487
Revises:
Create Date: 2024-03-04 15:11:38.840332+00:00

"""

__all__ = (
    "downgrade",
    "upgrade",
    "schema_upgrades",
    "schema_downgrades",
    "data_upgrades",
    "data_downgrades",
)

import warnings

import sqlalchemy as sa
from advanced_alchemy.types import (
    GUID,
    ORA_JSONB,
    DateTimeUTC,
    EncryptedString,
    EncryptedText,
)
from alembic import op

sa.GUID = GUID
sa.DateTimeUTC = DateTimeUTC
sa.ORA_JSONB = ORA_JSONB
sa.EncryptedString = EncryptedString
sa.EncryptedText = EncryptedText

# revision identifiers, used by Alembic.
revision = "c744e4868487"
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
    op.create_table(
        "user",
        sa.Column("login", sa.String(length=30), nullable=False),
        sa.Column("email", sa.String(length=50), nullable=False),
        sa.Column("hashedPassword", sa.LargeBinary(), nullable=False),
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
        "token",
        sa.Column("id", sa.GUID(length=16), nullable=False),
        sa.Column("user_login", sa.String(length=30), nullable=False),
        sa.Column("sa_orm_sentinel", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_login"],
            ["user.login"],
            name=op.f("fk_token_user_login_user"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_token")),
    )
    op.execute(sa.schema.CreateSequence(sa.Sequence("friend_id_seq")))


def schema_downgrades() -> None:
    """schema downgrade migrations go here."""
    op.drop_table("token")
    op.drop_table("friend")
    op.drop_table("user")
    op.execute(sa.schema.DropSequence(sa.Sequence("friend_id_seq")))


def data_upgrades() -> None:
    """Add any optional data upgrade migrations here!"""


def data_downgrades() -> None:
    """Add any optional data downgrade migrations here!"""

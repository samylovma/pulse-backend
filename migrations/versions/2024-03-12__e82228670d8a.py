# type: ignore
"""

Revision ID: e82228670d8a
Revises: b26271a94417
Create Date: 2024-03-12 17:07:06.070403+00:00

"""

from __future__ import annotations

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
from sqlalchemy import Text  # noqa: F401

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
revision = "e82228670d8a"
down_revision = "b26271a94417"
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
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("country_code", sa.String(length=2), nullable=False)
        )
        batch_op.add_column(sa.Column("is_public", sa.Boolean(), nullable=False))
        batch_op.create_unique_constraint(batch_op.f("uq_user_login"), ["login"])
        batch_op.drop_column("isPublic")
        batch_op.drop_column("countryCode")

    # ### end Alembic commands ###


def schema_downgrades() -> None:
    """schema downgrade migrations go here."""
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "countryCode",
                sa.VARCHAR(length=2),
                autoincrement=False,
                nullable=False,
            )
        )
        batch_op.add_column(
            sa.Column("isPublic", sa.BOOLEAN(), autoincrement=False, nullable=False)
        )
        batch_op.drop_constraint(batch_op.f("uq_user_login"), type_="unique")
        batch_op.drop_column("is_public")
        batch_op.drop_column("country_code")

    # ### end Alembic commands ###


def data_upgrades() -> None:
    """Add any optional data upgrade migrations here!"""


def data_downgrades() -> None:
    """Add any optional data downgrade migrations here!"""
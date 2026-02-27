"""Initial schema - core entities and framework content tables.

Revision ID: 20260227_0001
Revises:
Create Date: 2026-02-27
"""

from __future__ import annotations

import os
import sys

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260227_0001"
down_revision = None
branch_labels = None
depends_on = None


def _load_metadata():
    backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if backend_root not in sys.path:
        sys.path.insert(0, backend_root)

    from database import Base  # pylint: disable=import-outside-toplevel
    import models.database  # noqa: F401  # pylint: disable=import-outside-toplevel,unused-import

    return Base.metadata


def upgrade() -> None:
    metadata = _load_metadata()
    bind = op.get_bind()
    metadata.create_all(bind=bind)


def downgrade() -> None:
    metadata = _load_metadata()
    bind = op.get_bind()
    metadata.drop_all(bind=bind)

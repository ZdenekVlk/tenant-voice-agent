"""init schema

Revision ID: 212859f082d2
Revises: 
Create Date: 2025-12-29
"""
from alembic import op
from pathlib import Path

# revision identifiers, used by Alembic.
revision = "212859f082d2"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    sql_path = Path(__file__).resolve().parent.parent / "sql" / "schema.sql"
    sql = sql_path.read_text(encoding="utf-8")
    op.execute(sql)


def downgrade() -> None:
    raise NotImplementedError("Downgrade not supported for init schema.")

"""add idempotency keys

Revision ID: 6b1c4c2f8a47
Revises: 212859f082d2
Create Date: 2026-01-01
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "6b1c4c2f8a47"
down_revision = "212859f082d2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "idempotency_keys",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("key", sa.Text(), nullable=False),
        sa.Column("request_hash", sa.Text(), nullable=False),
        sa.Column("response_json", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_idempotency_keys"),
        sa.UniqueConstraint(
            "tenant_id",
            "conversation_id",
            "key",
            name="uq_idempotency_keys__tenant_id__conversation_id__key",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            name="fk_idempotency_keys__tenant_id__tenants",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "conversation_id"],
            ["conversations.tenant_id", "conversations.id"],
            name="fk_idempotency_keys__tenant_id_conversation_id__conversations",
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_idempotency_keys__tenant_id__conversation_id__created_at",
        "idempotency_keys",
        ["tenant_id", "conversation_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_idempotency_keys__tenant_id__conversation_id__created_at",
        table_name="idempotency_keys",
    )
    op.drop_table("idempotency_keys")

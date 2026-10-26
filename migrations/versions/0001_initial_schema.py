"""Initial legacy-compatible transactional schema.

Revision ID: 0001
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "transactions",
        sa.Column("transaction_id", sa.String(80), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("fraud_probability", sa.Float(), nullable=False),
        sa.Column("risk_score", sa.Integer(), nullable=False),
        sa.Column("risk_level", sa.String(10), nullable=False),
        sa.Column("is_flagged", sa.Boolean(), nullable=False),
        sa.Column("model_version", sa.String(100), nullable=False),
        sa.Column("reasons", sa.JSON(), nullable=False),
    )
    op.create_index("ix_transactions_created_at", "transactions", ["created_at"])


def downgrade():
    op.drop_index("ix_transactions_created_at", table_name="transactions")
    op.drop_table("transactions")

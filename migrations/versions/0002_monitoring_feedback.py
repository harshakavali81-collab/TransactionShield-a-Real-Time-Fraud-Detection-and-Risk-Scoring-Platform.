"""Add bounded numeric snapshots and clearly labeled demo review feedback.

Revision ID: 0002
Revises: 0001
"""
from alembic import op
import sqlalchemy as sa

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('transactions', sa.Column('numeric_features', sa.JSON(), nullable=True))
    op.create_table(
        'demo_review_feedback',
        sa.Column('transaction_id', sa.String(80), primary_key=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('review_label', sa.Boolean(), nullable=False),
        sa.Column('reviewer_note', sa.String(300), nullable=False),
    )


def downgrade():
    op.drop_table('demo_review_feedback')
    op.drop_column('transactions', 'numeric_features')

"""Add notified_created_at column on order

Revision ID: add_order_notified_created_at
Revises: add_payalert_and_variant_stock
Create Date: 2026-11-23 12:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'add_order_notified_created_at'
down_revision = 'add_payalert_and_variant_stock'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('notified_created_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.drop_column('notified_created_at')

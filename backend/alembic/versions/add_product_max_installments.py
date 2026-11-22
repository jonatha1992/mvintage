"""Add product.max_installments

Revision ID: add_product_max_installments
Revises: add_user_profile_fields
Create Date: 2026-11-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'add_product_max_installments'
down_revision = 'add_user_profile_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('max_installments', sa.Integer(), nullable=False, server_default='3'))


def downgrade() -> None:
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_column('max_installments')

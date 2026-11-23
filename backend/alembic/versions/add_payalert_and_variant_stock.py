"""Add PayAlert payment columns on order and variant_id on orderitem

Revision ID: add_payalert_and_variant_stock
Revises: add_product_max_installments
Create Date: 2026-11-22 23:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'add_payalert_and_variant_stock'
down_revision = 'add_product_max_installments'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('orderitem', schema=None) as batch_op:
        batch_op.add_column(sa.Column('variant_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_orderitem_variant_id_productvariant',
            'productvariant',
            ['variant_id'],
            ['id'],
        )

    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('mercadopago_checkout_url', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('payment_expires_at', sa.DateTime(), nullable=True))
        batch_op.add_column(
            sa.Column('stock_released', sa.Boolean(), nullable=False, server_default=sa.false())
        )


def downgrade() -> None:
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.drop_column('stock_released')
        batch_op.drop_column('payment_expires_at')
        batch_op.drop_column('mercadopago_checkout_url')

    with op.batch_alter_table('orderitem', schema=None) as batch_op:
        batch_op.drop_constraint('fk_orderitem_variant_id_productvariant', type_='foreignkey')
        batch_op.drop_column('variant_id')

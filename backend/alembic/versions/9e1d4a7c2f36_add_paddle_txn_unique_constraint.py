"""add unique constraint on credit_transactions.paddle_transaction_id

Revision ID: 9e1d4a7c2f36
Revises: 7a2f9c4e6b81
Create Date: 2026-07-22 00:05:00.000000
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '9e1d4a7c2f36'
down_revision = '7a2f9c4e6b81'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Prevents a retried/duplicate Paddle webhook delivery from crediting
    # the same purchase twice, even if two deliveries arrive concurrently.
    # Postgres allows multiple NULLs in a unique index, so non-Paddle
    # transactions (bonus/consumption/refund) are unaffected.
    op.create_unique_constraint(
        'uq_credit_transactions_paddle_transaction_id',
        'credit_transactions',
        ['paddle_transaction_id'],
    )


def downgrade() -> None:
    op.drop_constraint(
        'uq_credit_transactions_paddle_transaction_id',
        'credit_transactions',
        type_='unique',
    )

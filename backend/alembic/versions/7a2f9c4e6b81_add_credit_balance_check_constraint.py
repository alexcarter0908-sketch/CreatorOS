"""add non-negative check constraint to billing_accounts.credit_balance

Revision ID: 7a2f9c4e6b81
Revises: f3c8b91d4a20
Create Date: 2026-07-22 00:00:00.000000
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '7a2f9c4e6b81'
down_revision = 'f3c8b91d4a20'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Defense-in-depth: even if an application bug ever bypasses the
    # service-layer balance check, the database itself will refuse to let
    # credit_balance go negative.
    op.create_check_constraint(
        'ck_billing_accounts_credit_balance_non_negative',
        'billing_accounts',
        'credit_balance >= 0',
    )


def downgrade() -> None:
    op.drop_constraint(
        'ck_billing_accounts_credit_balance_non_negative',
        'billing_accounts',
        type_='check',
    )

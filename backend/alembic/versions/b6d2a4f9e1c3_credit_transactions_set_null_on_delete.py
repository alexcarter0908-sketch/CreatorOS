"""preserve credit_transactions on user deletion (CASCADE -> SET NULL)

Revision ID: b6d2a4f9e1c3
Revises: 9e1d4a7c2f36
Create Date: 2026-07-24 00:00:00.000000

Previously, deleting a user's account cascade-deleted their entire
credit_transactions ledger along with them - meaning every purchase,
refund, and consumption record vanished permanently. That's a real gap
for accounting/dispute-resolution purposes (e.g. a Paddle chargeback
investigation after the user has deleted their account).

This migration makes user_id nullable and switches the foreign key to
ON DELETE SET NULL, so deleting an account anonymizes the link to the
user while keeping the financial record itself intact.
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'b6d2a4f9e1c3'
down_revision = '9e1d4a7c2f36'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE credit_transactions "
        "DROP CONSTRAINT IF EXISTS credit_transactions_user_id_fkey"
    )
    op.execute(
        "ALTER TABLE credit_transactions ALTER COLUMN user_id DROP NOT NULL"
    )
    op.execute(
        "ALTER TABLE credit_transactions "
        "ADD CONSTRAINT credit_transactions_user_id_fkey "
        "FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL"
    )


def downgrade() -> None:
    # Not reversible without data loss: rows with user_id already NULL
    # (from a real account deletion) would violate a re-added NOT NULL
    # constraint. Left as a no-op deliberately.
    pass
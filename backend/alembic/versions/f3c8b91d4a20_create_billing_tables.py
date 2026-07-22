"""create billing_accounts and credit_transactions tables

Revision ID: f3c8b91d4a20
Revises: d12191c4f3c1
Create Date: 2026-07-22 00:10:00.000000

These tables have existed since the billing feature shipped, but were
only ever created via Base.metadata.create_all() at app startup, never
through an Alembic migration. That works today only because create_all()
happens to run before anyone runs `alembic upgrade head`. A database
provisioned purely from migration history (the standard, professional
way to stand up a fresh environment) would be missing these tables
entirely, and the two migrations that follow this one (which ALTER these
tables to add constraints) would fail outright.

This migration closes that gap. It's spliced in as this app's real
ancestor - `7a2f9c4e6b81` (add_credit_balance_check_constraint) now
points to this revision instead of directly to `d12191c4f3c1`. For any
database that already has these tables (i.e. every environment running
today), `IF NOT EXISTS` makes this a safe no-op.
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'f3c8b91d4a20'
down_revision = 'd12191c4f3c1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS billing_accounts (
            id VARCHAR NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            user_id VARCHAR NOT NULL,
            credit_balance INTEGER NOT NULL DEFAULT 0,
            free_quota_used_today INTEGER NOT NULL DEFAULT 0,
            free_quota_date VARCHAR(10),
            PRIMARY KEY (id),
            CONSTRAINT uq_billing_accounts_user_id UNIQUE (user_id),
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_billing_accounts_user_id "
        "ON billing_accounts (user_id)"
    )

    op.execute("""
        CREATE TABLE IF NOT EXISTS credit_transactions (
            id VARCHAR NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            user_id VARCHAR NOT NULL,
            type VARCHAR(30) NOT NULL,
            amount INTEGER NOT NULL,
            balance_after INTEGER NOT NULL,
            description TEXT,
            asset_id VARCHAR,
            paddle_transaction_id VARCHAR(255),
            PRIMARY KEY (id),
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (asset_id) REFERENCES assets (id) ON DELETE SET NULL
        )
    """)
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_credit_transactions_user_id "
        "ON credit_transactions (user_id)"
    )


def downgrade() -> None:
    # Deliberately a no-op. Downgrading would drop tables holding real
    # financial ledger data - too destructive to do implicitly.
    pass

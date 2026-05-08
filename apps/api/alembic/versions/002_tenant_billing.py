"""tenant billing columns for Stripe B2B

revision ID: 002_tenant_billing
Revises: 001_initial
"""

revision = "002_tenant_billing"
down_revision = "001_initial"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.add_column("tenants", sa.Column("stripe_customer_id", sa.String(64), nullable=True))
    op.add_column("tenants", sa.Column("stripe_subscription_id", sa.String(64), nullable=True))
    op.add_column("tenants", sa.Column("plan", sa.String(32), nullable=False, server_default="free"))
    op.add_column("tenants", sa.Column("subscription_status", sa.String(32), nullable=True))
    op.create_index("ix_tenants_stripe_customer_id", "tenants", ["stripe_customer_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_tenants_stripe_customer_id", table_name="tenants")
    op.drop_column("tenants", "subscription_status")
    op.drop_column("tenants", "plan")
    op.drop_column("tenants", "stripe_subscription_id")
    op.drop_column("tenants", "stripe_customer_id")

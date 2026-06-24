"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-06-23
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "businesses",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("phone_number", sa.String(30), unique=True, nullable=False),
        sa.Column("owner_email", sa.String(255), nullable=False),
        sa.Column("owner_phone", sa.String(30)),
        sa.Column("language", sa.String(10), nullable=False, server_default="en"),
        sa.Column("calendar_id", sa.String(255)),
        sa.Column("stripe_customer_id", sa.String(255)),
        sa.Column("stripe_subscription_id", sa.String(255)),
        sa.Column("plan", sa.String(20), nullable=False, server_default="starter"),
        sa.Column("widget_primary_color", sa.String(10), server_default="#6366f1"),
        sa.Column("airtable_base_id", sa.String(255)),
        sa.Column("airtable_table_name", sa.String(255)),
        sa.Column("active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "services",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("business_id", UUID(as_uuid=False), sa.ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("duration_minutes", sa.Integer, nullable=False),
        sa.Column("price_usd", sa.Numeric(10, 2), nullable=False),
        sa.Column("active", sa.Boolean, nullable=False, server_default="true"),
    )
    op.create_index("ix_services_business_id", "services", ["business_id"])

    op.create_table(
        "business_hours",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("business_id", UUID(as_uuid=False), sa.ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("day_of_week", sa.String(10), nullable=False),
        sa.Column("open_time", sa.Time),
        sa.Column("close_time", sa.Time),
        sa.Column("is_closed", sa.Boolean, nullable=False, server_default="false"),
    )
    op.create_index("ix_business_hours_business_id", "business_hours", ["business_id"])

    op.create_table(
        "customers",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("business_id", UUID(as_uuid=False), sa.ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255)),
        sa.Column("phone", sa.String(30), nullable=False),
        sa.Column("email", sa.String(255)),
        sa.Column("language", sa.String(10), server_default="en"),
        sa.Column("last_appointment_at", sa.DateTime(timezone=True)),
        sa.Column("total_appointments", sa.Integer, server_default="0"),
        sa.Column("reengaged", sa.Boolean, server_default="false"),
        sa.Column("airtable_record_id", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_customers_business_id", "customers", ["business_id"])
    op.create_index("ix_customers_phone", "customers", ["phone"])

    op.create_table(
        "appointments",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("business_id", UUID(as_uuid=False), sa.ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("customer_id", UUID(as_uuid=False), sa.ForeignKey("customers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("service_id", UUID(as_uuid=False), sa.ForeignKey("services.id", ondelete="SET NULL"), nullable=True),
        sa.Column("service_name", sa.String(255), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_minutes", sa.Integer, nullable=False),
        sa.Column("calendar_event_id", sa.String(255)),
        sa.Column("status", sa.String(20), nullable=False, server_default="confirmed"),
        sa.Column("booked_via", sa.String(10), nullable=False, server_default="voice"),
        sa.Column("reminded_24h", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("reminded_1h", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("no_show_followed_up", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_appointments_business_id", "appointments", ["business_id"])
    op.create_index("ix_appointments_start_at", "appointments", ["start_at"])
    op.create_index("ix_appointments_status", "appointments", ["status"])

    op.create_table(
        "sessions",
        sa.Column("id", sa.String(255), primary_key=True),
        sa.Column("business_id", UUID(as_uuid=False), sa.ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("customer_id", UUID(as_uuid=False), sa.ForeignKey("customers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("appointment_id", UUID(as_uuid=False), sa.ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("caller_number", sa.String(30), nullable=False),
        sa.Column("channel", sa.String(10), nullable=False, server_default="voice"),
        sa.Column("language", sa.String(10), nullable=False, server_default="en"),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("ended_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_sessions_business_id", "sessions", ["business_id"])
    op.create_index("ix_sessions_caller_number", "sessions", ["caller_number"])
    op.create_index("ix_sessions_created_at", "sessions", ["created_at"])

    op.create_table(
        "messages",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("session_id", sa.String(255), sa.ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(10), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_messages_session_id", "messages", ["session_id"])

    op.create_table(
        "missed_calls",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("business_id", UUID(as_uuid=False), sa.ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("caller_number", sa.String(30), nullable=False),
        sa.Column("recovered", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_missed_calls_business_id", "missed_calls", ["business_id"])

    op.create_table(
        "billing_events",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("business_id", UUID(as_uuid=False), sa.ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("stripe_event_id", sa.String(255), unique=True, nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("amount_cents", sa.Integer),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_billing_events_business_id", "billing_events", ["business_id"])


def downgrade() -> None:
    op.drop_table("billing_events")
    op.drop_table("missed_calls")
    op.drop_table("messages")
    op.drop_table("sessions")
    op.drop_table("appointments")
    op.drop_table("customers")
    op.drop_table("business_hours")
    op.drop_table("services")
    op.drop_table("businesses")

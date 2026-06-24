import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer,
    Numeric, String, Text, Time,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


def _uuid():
    return str(uuid.uuid4())


def _now():
    return datetime.now(timezone.utc)


class Business(Base):
    __tablename__ = "businesses"

    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    name = Column(String(255), nullable=False)
    phone_number = Column(String(30), unique=True, nullable=False)
    owner_email = Column(String(255), nullable=False)
    owner_phone = Column(String(30))
    language = Column(String(10), nullable=False, default="en")
    calendar_id = Column(String(255))
    stripe_customer_id = Column(String(255))
    stripe_subscription_id = Column(String(255))
    plan = Column(String(20), nullable=False, default="starter")
    widget_primary_color = Column(String(10), default="#6366f1")
    airtable_base_id = Column(String(255))
    airtable_table_name = Column(String(255))
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)

    services = relationship("Service", back_populates="business", cascade="all, delete-orphan")
    hours = relationship("BusinessHour", back_populates="business", cascade="all, delete-orphan")
    customers = relationship("Customer", back_populates="business")
    sessions = relationship("Session", back_populates="business")
    appointments = relationship("Appointment", back_populates="business")
    missed_calls = relationship("MissedCall", back_populates="business")
    billing_events = relationship("BillingEvent", back_populates="business")


class Service(Base):
    __tablename__ = "services"

    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    business_id = Column(UUID(as_uuid=False), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    price_usd = Column(Numeric(10, 2), nullable=False)
    active = Column(Boolean, nullable=False, default=True)

    business = relationship("Business", back_populates="services")
    appointments = relationship("Appointment", back_populates="service")


class BusinessHour(Base):
    __tablename__ = "business_hours"

    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    business_id = Column(UUID(as_uuid=False), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    day_of_week = Column(String(10), nullable=False)  # monday … sunday
    open_time = Column(Time)
    close_time = Column(Time)
    is_closed = Column(Boolean, nullable=False, default=False)

    business = relationship("Business", back_populates="hours")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    business_id = Column(UUID(as_uuid=False), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255))
    phone = Column(String(30), nullable=False)
    email = Column(String(255))
    language = Column(String(10), default="en")
    last_appointment_at = Column(DateTime(timezone=True))
    total_appointments = Column(Integer, default=0)
    reengaged = Column(Boolean, default=False)
    airtable_record_id = Column(String(255))
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)

    business = relationship("Business", back_populates="customers")
    appointments = relationship("Appointment", back_populates="customer")
    sessions = relationship("Session", back_populates="customer")


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    business_id = Column(UUID(as_uuid=False), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(UUID(as_uuid=False), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)
    service_id = Column(UUID(as_uuid=False), ForeignKey("services.id", ondelete="SET NULL"), nullable=True)
    service_name = Column(String(255), nullable=False)  # denormalized for history
    start_at = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    calendar_event_id = Column(String(255))
    status = Column(String(20), nullable=False, default="confirmed")  # confirmed|cancelled|completed|no_show
    booked_via = Column(String(10), nullable=False, default="voice")  # voice|sms|web
    reminded_24h = Column(Boolean, nullable=False, default=False)
    reminded_1h = Column(Boolean, nullable=False, default=False)
    no_show_followed_up = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)

    business = relationship("Business", back_populates="appointments")
    customer = relationship("Customer", back_populates="appointments")
    service = relationship("Service", back_populates="appointments")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String(255), primary_key=True)  # Twilio CallSid or web-<uuid>
    business_id = Column(UUID(as_uuid=False), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(UUID(as_uuid=False), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)
    appointment_id = Column(UUID(as_uuid=False), ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True)
    caller_number = Column(String(30), nullable=False)
    channel = Column(String(10), nullable=False, default="voice")  # voice|sms|web
    language = Column(String(10), nullable=False, default="en")
    status = Column(String(20), nullable=False, default="active")  # active|completed|transferred|missed
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)
    ended_at = Column(DateTime(timezone=True))

    business = relationship("Business", back_populates="sessions")
    customer = relationship("Customer", back_populates="sessions")
    messages = relationship("Message", back_populates="session", order_by="Message.created_at", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    session_id = Column(String(255), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(10), nullable=False)   # user | model
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)

    session = relationship("Session", back_populates="messages")


class MissedCall(Base):
    __tablename__ = "missed_calls"

    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    business_id = Column(UUID(as_uuid=False), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    caller_number = Column(String(30), nullable=False)
    recovered = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)

    business = relationship("Business", back_populates="missed_calls")


class BillingEvent(Base):
    __tablename__ = "billing_events"

    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    business_id = Column(UUID(as_uuid=False), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    stripe_event_id = Column(String(255), unique=True, nullable=False)
    event_type = Column(String(100), nullable=False)
    amount_cents = Column(Integer)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)

    business = relationship("Business", back_populates="billing_events")

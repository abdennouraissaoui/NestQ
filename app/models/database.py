"""
Database models for the application.
"""

from app.services.db_connection_manager import DBConnectionManager
import uuid
from sqlalchemy.orm import declarative_base
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    Integer,
    Float,
    DateTime,
    Boolean,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

Base = declarative_base()


class Firm(Base):
    __tablename__ = "firm"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    enabled = Column(Boolean, default=True, nullable=False)
    users = relationship("User", back_populates="firm")


class User(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firm_id = Column(UUID(as_uuid=True), ForeignKey("firm.id"), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("role.id"), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)
    referred_by_user_id = Column(
        UUID(as_uuid=True), ForeignKey("user.id"), nullable=True
    )
    last_login = Column(DateTime, nullable=True)
    sign_in_count = Column(Integer, default=0, nullable=False)
    last_sign_in_at = Column(DateTime, nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    is_deleted_at = Column(DateTime, nullable=True)
    is_deleted_by = Column(UUID(as_uuid=True), nullable=True)

    firm = relationship("Firm", back_populates="users")
    clients = relationship(
        "Client", back_populates="advisor", foreign_keys="Client.advisor_id"
    )
    referred_users = relationship("User", backref="referred_by", remote_side=[id])
    advisor = relationship("Advisor", uselist=False, back_populates="user")


class Role(Base):
    __tablename__ = "role"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    users = relationship("User", back_populates="role")


class Client(Base):
    __tablename__ = "client"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    advisor_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    is_deleted = Column(Boolean, default=False, nullable=False)

    advisor = relationship("User", back_populates="clients")
    accounts = relationship("Account", back_populates="client")
    addresses = relationship("Address", back_populates="client")
    scans = relationship("Scan", back_populates="client")


class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("client.id"), nullable=False)
    account_number = Column(String(50), nullable=False, unique=True)
    account_type = Column(String(50), nullable=False)
    fee_id = Column(UUID(as_uuid=True), ForeignKey("fee.id"), nullable=True)
    currency = Column(String(10), nullable=False)
    institution = Column(String(100), nullable=False)
    cash_balance = Column(Float, default=0.0, nullable=False)
    risk_profile = Column(String(50), nullable=True)
    benchmark = Column(String(50), nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    is_deleted = Column(Boolean, default=False, nullable=False)

    client = relationship("Client", back_populates="accounts")
    holdings = relationship("Holding", back_populates="account")


class Address(Base):
    __tablename__ = "addresses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("client.id"), nullable=False)
    unit_number = Column(String(10), nullable=True)
    street_number = Column(String(10), nullable=False)
    street_name = Column(String(100), nullable=False)
    city = Column(String(50), nullable=False)
    state = Column(String(50), nullable=False)
    postal_code = Column(String(10), nullable=False)
    country = Column(String(50), nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    client = relationship("Client", back_populates="addresses")


class Advisor(Base):
    __tablename__ = "advisor"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    subscription_id = Column(
        UUID(as_uuid=True), ForeignKey("subscription.id"), nullable=True
    )
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    is_deleted = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="advisor")
    subscriptions = relationship("Subscription", back_populates="advisor")


class Holding(Base):
    __tablename__ = "holdings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("asset.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    cost_per_share = Column(Float, nullable=False)
    current_price = Column(Float, nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    account = relationship("Account", back_populates="holdings")
    asset = relationship("Asset", back_populates="holdings")


class Asset(Base):
    __tablename__ = "asset"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    symbol = Column(String(10), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    holdings = relationship("Holding", back_populates="asset")


class Subscription(Base):
    __tablename__ = "subscription"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    advisor_id = Column(UUID(as_uuid=True), ForeignKey("advisor.id"), nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plan.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    is_deleted = Column(Boolean, default=False, nullable=False)

    advisor = relationship("Advisor", back_populates="subscriptions")
    payments = relationship("Payment", back_populates="subscription")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(
        UUID(as_uuid=True), ForeignKey("subscription.id"), nullable=False
    )
    amount = Column(Float, nullable=False)
    payment_date = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    payment_method = Column(String(50), nullable=False)
    payment_status = Column(String(50), nullable=False)

    subscription = relationship("Subscription", back_populates="payments")


class Scan(Base):
    __tablename__ = "scans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("client.id"), nullable=False)
    uploaded_file = Column(String(255), nullable=False)
    page_count = Column(Integer, nullable=False)
    file_name = Column(String(255), nullable=False)
    ocr_source = Column(String(50), nullable=True)
    ocr_id = Column(String(255), nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    client = relationship("Client", back_populates="scans")


class Plan(Base):
    __tablename__ = "plan"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    fee = Column(Float, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    subscriptions = relationship("Subscription", back_populates="plan")


class Fee(Base):
    __tablename__ = "fee"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    accounts = relationship("Account", back_populates="fee")


# Create tables in the database

dbcm = DBConnectionManager()
conn = dbcm.get_connection()
Base.metadata.create_all(conn)
conn.commit()
dbcm.close_all_connections()

"""
Database models for the application.
Models must always be in sync with the database.
"""

from sqlalchemy.orm import declarative_base
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    Integer,
    Float,
    Boolean,
    Text,
    Index,
    BigInteger,
    Enum,
    LargeBinary,
)
from sqlalchemy.dialects.postgresql import JSONB, BYTEA
from sqlalchemy.orm import relationship
import time
from app.models.enums import (
    AccountType,
    AuditLogAction,
    SubscriptionStatus,
    SubscriptionTier,
    ScanStatus,
    Role,
)
from sqlalchemy.types import TypeDecorator, TEXT


Base = declarative_base()


def utc_timestamp():
    return int(time.time())


class Firm(Base):
    __tablename__ = "firms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(BigInteger, default=utc_timestamp, nullable=False)
    updated_at = Column(
        BigInteger, default=utc_timestamp, onupdate=utc_timestamp, nullable=False
    )
    enabled = Column(Boolean, default=True, nullable=False)
    users = relationship("User", back_populates="firm")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    firm_id = Column(Integer, ForeignKey("firms.id"), nullable=False)
    role = Column(Enum(Role), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(LargeBinary, nullable=False)
    phone_number = Column(String(20), nullable=True)
    referred_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    last_login = Column(BigInteger, nullable=True)
    sign_in_count = Column(Integer, default=0, nullable=False)
    created_at = Column(BigInteger, default=utc_timestamp, nullable=False)
    created_by = Column(Integer, nullable=True)
    updated_at = Column(
        BigInteger, default=utc_timestamp, onupdate=utc_timestamp, nullable=False
    )
    firm = relationship("Firm", back_populates="users")
    referred_users = relationship("User", back_populates="referred_by")
    referred_by = relationship(
        "User", back_populates="referred_users", remote_side=[id]
    )
    advisor = relationship("Advisor", uselist=False, back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

    __table_args__ = (Index("ix_user_firm_id", "firm_id"),)


class JSONType(TypeDecorator):
    impl = TEXT

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(TEXT())


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    table_name = Column(String(100), nullable=False)
    record_id = Column(Integer, nullable=False)
    action = Enum(AuditLogAction, nullable=False)
    old_data = Column(JSONType, nullable=True)
    new_data = Column(JSONType, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    timestamp = Column(BigInteger, default=utc_timestamp, nullable=False)
    user = relationship("User", back_populates="audit_logs")
    __table_args__ = (
        Index("ix_audit_log_table_name_record_id", "table_name", "record_id"),
        Index("ix_audit_log_timestamp", "timestamp"),
    )


class Advisor(Base):
    __tablename__ = "advisors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    created_at = Column(BigInteger, default=utc_timestamp, nullable=False)
    updated_at = Column(
        BigInteger, default=utc_timestamp, onupdate=utc_timestamp, nullable=False
    )
    user = relationship("User", back_populates="advisor")
    subscription = relationship("Subscription", back_populates="advisor", uselist=False)
    prospects = relationship("Prospect", back_populates="advisor")
    __table_args__ = (Index("ix_advisors_user_id", "user_id"),)


class Prospect(Base):
    __tablename__ = "prospects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    advisor_id = Column(Integer, ForeignKey("advisors.id"), nullable=False)
    created_at = Column(BigInteger, default=utc_timestamp, nullable=False)
    updated_at = Column(
        BigInteger, default=utc_timestamp, onupdate=utc_timestamp, nullable=False
    )

    advisor = relationship("Advisor", back_populates="prospects")
    accounts = relationship("Account", back_populates="prospect")
    addresses = relationship("Address", back_populates="prospect")
    scans = relationship("Scan", back_populates="prospect")
    __table_args__ = (Index("ix_prospects_advisor_id", "advisor_id"),)


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prospect_id = Column(Integer, ForeignKey("prospects.id"), nullable=False)
    unit_number = Column(String(10), nullable=True)
    street_number = Column(String(10), nullable=False)
    street_name = Column(String(100), nullable=False)
    city = Column(String(50), nullable=False)
    state = Column(String(50), nullable=False)
    postal_code = Column(String(10), nullable=False)
    country = Column(String(50), nullable=False)
    created_at = Column(BigInteger, default=utc_timestamp, nullable=False)
    updated_at = Column(
        BigInteger, default=utc_timestamp, onupdate=utc_timestamp, nullable=False
    )
    __table_args__ = (Index("ix_addresses_prospect_id", "prospect_id"),)
    prospect = relationship("Prospect", back_populates="addresses")


class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    symbol = Column(String(20), nullable=True)
    description = Column(String(255), nullable=False)
    cusip = Column(String(9), nullable=True)
    quantity = Column(Float, nullable=True)
    book_value = Column(Float, nullable=True)
    cost_per_share = Column(Float, nullable=True)
    market_value = Column(Float, nullable=False)
    current_price = Column(Float, nullable=True)
    currency = Column(String(3), nullable=False)
    created_at = Column(BigInteger, default=utc_timestamp, nullable=False)
    updated_at = Column(
        BigInteger, default=utc_timestamp, onupdate=utc_timestamp, nullable=False
    )

    account = relationship("Account", back_populates="holdings")
    asset = relationship("Asset", back_populates="holdings")
    __table_args__ = (
        Index("ix_holdings_account_id", "account_id"),
        Index("ix_holdings_asset_id", "asset_id"),
        Index("ix_holdings_cusip", "cusip"),
    )


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    symbol = Column(String(10), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(BigInteger, default=utc_timestamp, nullable=False)
    updated_at = Column(
        BigInteger, default=utc_timestamp, onupdate=utc_timestamp, nullable=False
    )

    holdings = relationship("Holding", back_populates="asset")


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prospect_id = Column(Integer, ForeignKey("prospects.id"), nullable=False)
    account_number = Column(String(50), nullable=False, unique=True)
    account_type = Column(Enum(AccountType), nullable=False)
    currency = Column(String(3), nullable=False)
    institution = Column(String(100), nullable=False)
    management_fee_amount = Column(Float, nullable=True)
    created_at = Column(BigInteger, default=utc_timestamp, nullable=False)
    updated_at = Column(
        BigInteger, default=utc_timestamp, onupdate=utc_timestamp, nullable=False
    )
    prospect = relationship("Prospect", back_populates="accounts")
    holdings = relationship("Holding", back_populates="account")
    __table_args__ = (
        Index("ix_accounts_prospect_id", "prospect_id"),
        Index("ix_accounts_account_number", "account_number"),
    )


class AssetAllocation(Base):
    __tablename__ = "asset_allocations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    asset_class = Column(String(100), nullable=False)
    percentage = Column(Float, nullable=False)
    created_at = Column(BigInteger, default=utc_timestamp, nullable=False)
    updated_at = Column(
        BigInteger, default=utc_timestamp, onupdate=utc_timestamp, nullable=False
    )

    scan = relationship("Scan", back_populates="asset_allocations")

    __table_args__ = (Index("ix_asset_allocations_scan_id", "scan_id"),)

    def __repr__(self):
        return f"<AssetAllocation(id={self.id}, scan_id={self.scan_id}, asset_class={self.asset_class}, percentage={self.percentage})>"


class Performance(Base):
    __tablename__ = "performances"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    period = Column(String(50), nullable=False)
    return_percentage = Column(Float, nullable=False)
    benchmark = Column(String(100), nullable=True)
    benchmark_return_percentage = Column(Float, nullable=True)
    created_at = Column(BigInteger, default=utc_timestamp, nullable=False)
    updated_at = Column(
        BigInteger, default=utc_timestamp, onupdate=utc_timestamp, nullable=False
    )

    scan = relationship("Scan", back_populates="performances")

    __table_args__ = (Index("ix_performances_scan_id", "scan_id"),)

    def __repr__(self):
        return f"<Performance(id={self.id}, scan_id={self.scan_id}, period={self.period}, return_percentage={self.return_percentage})>"


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prospect_id = Column(Integer, ForeignKey("prospects.id"), nullable=False)
    uploaded_file = Column(BYTEA, nullable=False)
    page_count = Column(Integer, nullable=False)
    file_name = Column(String(255), nullable=False)
    ocr_source = Column(String(50), nullable=False)
    status = Column(Enum(ScanStatus), nullable=False)
    ocr_text = Column(Text, nullable=False)
    ocr_text_cleaned = Column(Text, nullable=False)
    processing_time = Column(Float, nullable=True)
    created_at = Column(BigInteger, default=utc_timestamp, nullable=False)
    updated_at = Column(
        BigInteger, default=utc_timestamp, onupdate=utc_timestamp, nullable=False
    )

    prospect = relationship("Prospect", back_populates="scans")
    asset_allocations = relationship("AssetAllocation", back_populates="scan")
    performances = relationship("Performance", back_populates="scan")
    __table_args__ = (
        Index("ix_scans_prospect_id", "prospect_id"),
        Index("ix_scans_status", "status"),
    )


class Subscription(Base):
    # https://courses.bigbinaryacademy.com/handling-stripe-subscriptions/designing-database-for-subscription/
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    advisor_id = Column(Integer, ForeignKey("advisors.id"), nullable=False, unique=True)
    stripe_subscription_id = Column(String(255), unique=True, nullable=False)
    status = Column(Enum(SubscriptionStatus), nullable=False)
    tier = Column(Enum(SubscriptionTier), nullable=False)
    current_period_start = Column(BigInteger, nullable=False)
    current_period_end = Column(BigInteger, nullable=False)
    cancel_at_period_end = Column(Boolean, default=False)
    cancel_at = Column(BigInteger, nullable=True)
    canceled_at = Column(BigInteger, nullable=True)
    ended_at = Column(BigInteger, nullable=True)
    default_payment_method = Column(String(255), nullable=True)
    attributes = Column(JSONType, nullable=True)
    created_at = Column(BigInteger, default=utc_timestamp, nullable=False)
    updated_at = Column(
        BigInteger, default=utc_timestamp, onupdate=utc_timestamp, nullable=False
    )

    advisor = relationship("Advisor", back_populates="subscription")
    prices = relationship("Price", back_populates="subscription")
    __table_args__ = (
        Index("ix_subscriptions_advisor_id", "advisor_id"),
        Index("ix_subscriptions_stripe_subscription_id", "stripe_subscription_id"),
        Index("ix_subscriptions_status", "status"),
    )

    def __repr__(self):
        return f"<Subscription(id={self.id}, advisor_id={self.advisor_id}, status={self.status}, tier={self.tier})>"


class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    stripe_price_id = Column(String(255), unique=True, nullable=False)
    stripe_product_id = Column(String(255), nullable=False)
    amount = Column(Integer, nullable=False)
    label = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    attributes = Column(JSONType, nullable=True)
    created_at = Column(BigInteger, default=utc_timestamp, nullable=False)
    updated_at = Column(
        BigInteger, default=utc_timestamp, onupdate=utc_timestamp, nullable=False
    )

    subscription = relationship("Subscription", back_populates="prices")

    __table_args__ = (
        Index("ix_prices_stripe_price_id", "stripe_price_id"),
        Index("ix_prices_stripe_product_id", "stripe_product_id"),
        Index("ix_prices_subscription_id", "subscription_id"),
    )

    def __repr__(self):
        return f"<Price(id={self.id}, stripe_price_id={self.stripe_price_id}, amount={self.amount})>"


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    external_event_id = Column(String(255), unique=True, nullable=False)
    event_type = Column(String(255), nullable=False)
    data = Column(JSONType, nullable=False)

    def __repr__(self):
        return f"<WebhookEvent(id={self.id}, stripe_event_id={self.stripe_event_id}, event_type={self.event_type}, processed={self.processed})>"


# Create tables in the database
if __name__ == "__main__":
    from utils.db_connection_manager import engine

    Base.metadata.create_all(engine)

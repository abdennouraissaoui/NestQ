import json
from app.models.database import (
    Firm,
    User,
    AuditLog,
    Role,
    Advisor,
    Client,
    Address,
    Holding,
    Account,
    Asset,
    Scan,
    Subscription,
    Price,
    WebhookEvent,
)
from app.models.enums import (
    AccountType,
    AuditLogAction,
    SubscriptionStatus,
    SubscriptionTier,
    ScanStatus,
)
from app.services.db_connection_manager import DBConnectionManager
import uuid
import random
from datetime import datetime, timedelta

dbcm = DBConnectionManager()
session = dbcm.get_session()


# Helper function to generate random dates
def random_date(start, end):
    return start + timedelta(
        seconds=random.randint(0, int((end - start).total_seconds()))
    )


# Create sample data for Firm
sample_firm = Firm(
    name="Sample Financial Advisors",
    description="A sample firm for testing purposes",
    enabled=True,
)
session.add(sample_firm)
session.flush()  # Add this line to flush the session

# Create sample data for Role
roles = [
    Role(name="Admin", description="Administrator role"),
    Role(name="Advisor", description="Financial advisor role"),
    Role(name="Client", description="Client role"),
]
session.add_all(roles)
session.flush()  # Add this line to ensure roles have IDs

# Create sample data for User and Advisor
users = []
advisors = []
for i in range(5):
    user = User(
        firm_id=sample_firm.id,
        role_id=roles[1].id,
        first_name=f"Advisor{i}",
        last_name=f"LastName{i}",
        email=f"advisor{i}@example.com",
        password="hashed_password",
        phone_number=f"+1555555{1000+i}",
    )
    users.append(user)
    session.add(user)
    session.flush()

    advisor = Advisor(user_id=user.id)
    advisors.append(advisor)
    session.add(advisor)

session.flush()  # Add this line to ensure users and advisors have IDs

# Create sample data for Client, Address, and Account
clients = []
for i in range(20):
    client = Client(
        first_name=f"Client{i}",
        last_name=f"LastName{i}",
        advisor_id=random.choice(users).id,
    )
    clients.append(client)
    session.add(client)
    session.flush()

    address = Address(
        client_id=client.id,
        street_number=str(random.randint(100, 999)),
        street_name="Main St",
        city="Anytown",
        state="CA",
        postal_code=f"9{random.randint(1000, 9999)}",
        country="USA",
    )
    session.add(address)

    account = Account(
        client_id=client.id,
        account_number=f"ACC{random.randint(10000, 99999)}",
        account_type=random.choice(list(AccountType)),
        currency="USD",
        institution="Sample Bank",
        management_fee_amount=random.uniform(0.5, 2.0),
    )
    session.add(account)

# Create sample data for Asset
sample_assets = [
    Asset(name="Apple Inc.", symbol="AAPL", description="Technology company"),
    Asset(
        name="Microsoft Corporation", symbol="MSFT", description="Technology company"
    ),
    Asset(
        name="Amazon.com Inc.",
        symbol="AMZN",
        description="E-commerce and cloud computing company",
    ),
    Asset(name="Alphabet Inc.", symbol="GOOGL", description="Technology company"),
    Asset(name="Facebook, Inc.", symbol="FB", description="Social media company"),
    Asset(
        name="Tesla, Inc.",
        symbol="TSLA",
        description="Electric vehicle and clean energy company",
    ),
    Asset(name="Johnson & Johnson", symbol="JNJ", description="Healthcare company"),
    Asset(
        name="JPMorgan Chase & Co.",
        symbol="JPM",
        description="Financial services company",
    ),
    Asset(name="Visa Inc.", symbol="V", description="Financial services company"),
    Asset(
        name="Procter & Gamble Co.", symbol="PG", description="Consumer goods company"
    ),
]

session.add_all(sample_assets)
session.flush()  # Ensure assets have IDs before creating holdings

# Update Holding creation to use the sample assets
for account in session.query(Account).all():
    for _ in range(random.randint(1, 5)):
        asset = random.choice(sample_assets)
        holding = Holding(
            account_id=account.id,
            asset_id=asset.id,
            symbol=asset.symbol,
            description=asset.description,
            cusip=f"{random.randint(100000000, 999999999)}",
            quantity=random.randint(1, 1000),
            book_value=random.uniform(1000, 10000),
            market_value=random.uniform(1000, 10000),
            current_price=random.uniform(10, 1000),
            currency="USD",
        )
        session.add(holding)

# Create sample data for Scan
for client in clients:
    scan = Scan(
        client_id=client.id,
        uploaded_file=f"scan_{uuid.uuid4()}.pdf",
        page_count=random.randint(1, 10),
        file_name=f"client_{client.id}_scan.pdf",
        ocr_source="tesseract",
        ocr_id=str(uuid.uuid4()),
        status=ScanStatus.PENDING.value,
        ocr_text="Sample OCR text",
        ocr_text_cleaned="Sample cleaned OCR text",
        processing_time=random.uniform(0.5, 5.0),
    )
    session.add(scan)

# Create sample data for Subscription and Price
for advisor in advisors:
    subscription = Subscription(
        advisor_id=advisor.id,
        stripe_subscription_id=f"sub_{uuid.uuid4().hex[:20]}",
        status=random.choice(list(SubscriptionStatus)),
        tier=random.choice(list(SubscriptionTier)),
        current_period_start=int(datetime.now().timestamp()),
        current_period_end=int((datetime.now() + timedelta(days=30)).timestamp()),
        cancel_at_period_end=False,
    )
    session.add(subscription)
    session.flush()

    price = Price(
        subscription_id=subscription.id,
        stripe_price_id=f"price_{uuid.uuid4().hex[:20]}",
        stripe_product_id=f"prod_{uuid.uuid4().hex[:20]}",
        amount=random.choice([1999, 4999, 9999]),
        label=f"{subscription.tier.name} Plan",
        description=f"Monthly subscription for {subscription.tier.name} tier",
    )
    session.add(price)

# Create sample data for WebhookEvent
for _ in range(5):
    webhook_event = WebhookEvent(
        external_event_id=f"evt_{uuid.uuid4().hex[:20]}",
        event_type=random.choice(
            [
                "customer.subscription.created",
                "customer.subscription.updated",
                "invoice.paid",
            ]
        ),
        data=json.dumps({"sample": "data"}),
        processed=random.choice([True, False]),
    )
    session.add(webhook_event)

# Create sample data for AuditLog
for _ in range(10):
    audit_log = AuditLog(
        table_name=random.choice(["users", "clients", "accounts", "subscriptions"]),
        record_id=uuid.uuid4(),
        action=random.choice(list(AuditLogAction)),
        old_data=json.dumps({"sample": "old_data"}),
        new_data=json.dumps({"sample": "new_data"}),
        user_id=random.choice(users).id,
    )
    session.add(audit_log)

# Commit the changes and close the session
session.commit()
session.close()
dbcm.close_all_connections()

print("Sample data has been added to the database.")

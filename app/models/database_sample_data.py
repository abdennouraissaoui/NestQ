# import json
from app.models.database.orm_models import (
    Firm,
    # User,
    # AuditLog,
    # Role,
    # Advisor,
    # Client,
    # Address,
    # Holding,
    # Account,
    # Asset,
    # Scan,
    # Subscription,
    # Price,
    # WebhookEvent,
)

# from app.models.enums import (
#     AccountType,
#     AuditLogAction,
#     SubscriptionStatus,
#     SubscriptionTier,
#     ScanStatus,
# )
from utils.db_connection_manager import get_db
import random
from datetime import timedelta

session = next(get_db())


# Helper function to generate random dates
def random_date(start, end):
    return start + timedelta(
        seconds=random.randint(0, int((end - start).total_seconds()))
    )


# Create sample data for Firm
sample_firm = Firm(
    name="ABC Wealth",
    description="Beta users",
    enabled=True,
)
session.add(sample_firm)
session.commit()  # Add this line to flush the session
session.close()


print("Sample data has been added to the database.")

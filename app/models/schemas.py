"""
Schemas for the data to be extracted from the financial statements.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ValidationInfo

from app.models.enums import AccountType


class Client(BaseModel):
    first_name: Optional[str] = Field(description="First name of the client")
    last_name: Optional[str] = Field(description="Last name of the client")
    client_unit_number: Optional[str] = Field(
        description="Unit number of the client's address"
    )
    client_street_number: Optional[str] = Field(
        description="Street number of the client's address"
    )
    client_street_name: Optional[str] = Field(
        description="Street name of the client's address"
    )
    client_city: Optional[str] = Field(description="City of the client's address")
    client_province: Optional[str] = Field(
        description="Province of the client's address"
    )
    client_postal_code: Optional[str] = Field(
        description="Postal code of the client's address"
    )
    client_country: Optional[str] = Field(description="Country of the client's address")


class Holding(BaseModel):
    symbol: Optional[str] = Field(description="Symbol or ticker of the investment")
    description: str = Field(description="Description or name of the investment")
    cusip: Optional[str] = Field(description="CUSIP of the investment")
    quantity: Optional[float] = Field(description="Quantity of the investment.")
    book_value: Optional[float] = Field(
        description="Book value or cost basis of the investment"
    )
    cost_per_share: Optional[float] = Field(
        description="Cost per share of the investment"
    )
    market_value: float = Field(description="Market value of the investment")
    current_price: Optional[float] = Field(
        description="Current price of the investment"
    )
    currency: str = Field(description="Currency of the holding")


class Account(BaseModel):
    account_id: Optional[str] = Field(description="ID of the account")
    account_type: AccountType = Field(description="Type of the account")
    cash_balance: Optional[float] = Field(description="Cash balance in the account")
    statement_start_date: Optional[str] = Field(
        description="Statement start date for the account"
    )
    statement_end_date: Optional[str] = Field(
        description="Statement end date for the account"
    )
    management_fee_amount: Optional[float] = Field(
        description="Management fee amount for the account"
    )
    holdings: List[Holding] = Field(description="List of holdings in the account")
    account_value: Optional[float] = Field(description="Total value of the account")

    @field_validator("account_value")
    @classmethod
    def validate_account_value(
        cls, account_value: Optional[float], info: ValidationInfo
    ) -> Optional[float]:
        if account_value is not None and "holdings" in info.data:
            total_holdings_value = sum(
                holding.market_value for holding in info.data["holdings"]
            )
            total_value = total_holdings_value + (info.data.get("cash_balance") or 0)
            if (
                abs(account_value - total_value) > 0.01
            ):  # Allow for small rounding differences
                raise ValueError(
                    f"Account value ({account_value}) does not match the sum of holdings market values "
                    f"({total_holdings_value}) plus cash balance ({info.data.get('cash_balance') or 0})"
                )
        return account_value


class FinancialStatement(BaseModel):
    client: Client = Field(description="Client information")
    accounts: List[Account] = Field(description="List of accounts")


def example_financial_statement() -> FinancialStatement:
    return FinancialStatement(
        client=Client(
            first_name="John",
            last_name="Doe",
            client_unit_number="123",
            client_street_number="123",
            client_street_name="Main St",
            client_city="Anytown",
            client_province="ON",
            client_postal_code="M1M1M1",
            client_country="Canada",
        ),
        accounts=[
            Account(
                account_id="ACC123456",
                account_type=AccountType.TFSA,
                account_value=50000.00,
                cash_balance=1000.00,
                statement_start_date="2023-01-01",
                statement_end_date="2023-03-31",
                management_fee_amount=125.00,
                holdings=[
                    Holding(
                        symbol="AAPL",
                        description="Apple Inc.",
                        quantity=50,
                        book_value=5000.00,
                        cost_per_share=100.00,
                        market_value=7500.00,
                        current_price=150.00,
                        currency="USD",
                        cusip="037833100",
                    ),
                    Holding(
                        symbol="GOOGL",
                        description="Alphabet Inc.",
                        quantity=10,
                        book_value=10000.00,
                        cost_per_share=1000.00,
                        market_value=41500.00,
                        current_price=4150.00,
                        currency="USD",
                        cusip="037833100",
                    ),
                ],
            )
        ],
    )


if __name__ == "__main__":
    # Validate the example
    example = example_financial_statement()

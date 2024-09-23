"""

Schemas for the data to be extracted from the financial statements.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from app.models.enums import AccountType
from app.models.enums import Role
from datetime import datetime


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
            if (
                abs(account_value - total_holdings_value) > 0.01
            ):  # Allow for small rounding differences
                raise ValueError(
                    f"Account value ({account_value}) does not match the sum of holdings market values "
                    f"({total_holdings_value})"
                )

        return account_value


class FinancialStatement(BaseModel):
    client: Client = Field(description="Client information")

    accounts: List[Account] = Field(description="List of accounts")


class UserBase(BaseModel):
    firm_id: int = Field(..., examples=[1])
    role: Role = Field(...)
    email: str = Field(
        ...,
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        examples=["test@example.com"],
    )
    first_name: str = Field(..., min_length=2, examples=["John"])
    last_name: str = Field(..., min_length=2, examples=["Doe"])
    password: str = Field(..., examples=["password"])
    phone_number: str = Field(..., examples=["6479700630"])


class UserDisplay(BaseModel):
    id: int
    role: str
    email: str
    first_name: str
    last_name: str
    phone_number: str

    class Config:
        from_attributes = True


class FirmDisplay(BaseModel):
    id: int
    name: str

    description: Optional[str]

    users: List[UserDisplay]

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class DocumentCreate(BaseModel):
    filename: str
    file_path: str


class DocumentResponse(BaseModel):
    id: int
    filename: str
    created_at: int
    user_id: int

    class Config:
        orm_mode = True

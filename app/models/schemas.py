from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from app.models.enums import AccountType
from app.models.enums import Role


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


class UserPut(BaseModel):
    firm_id: int = Field(..., examples=[1])
    email: str = Field(
        ...,
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        examples=["test@example.com"],
    )
    first_name: str = Field(..., min_length=2, examples=["John"])
    last_name: str = Field(..., min_length=2, examples=["Doe"])
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
        from_attributes = True


class Prospect(BaseModel):
    first_name: Optional[str] = Field(description="First name of the prospect")
    last_name: Optional[str] = Field(description="Last name of the prospect")
    advisor_id: int = Field(description="ID of the advisor")


class ProspectDisplay(BaseModel):
    id: int = Field(description="ID of the prospect", example=1)
    first_name: Optional[str] = Field(
        description="First name of the prospect", example="John"
    )
    last_name: Optional[str] = Field(
        description="Last name of the prospect", example="Doe"
    )
    created_at: int = Field(
        description="Timestamp when the prospect was created", example=1622547800
    )
    updated_at: int = Field(
        description="Timestamp when the prospect was last updated", example=1622547900
    )


class ProspectDetailDisplay(BaseModel):
    id: int = Field(description="ID of the prospect", example=1)
    first_name: Optional[str] = Field(
        description="First name of the prospect", example="John"
    )
    last_name: Optional[str] = Field(
        description="Last name of the prospect", example="Doe"
    )
    documents: List[str] = Field(
        description="List of document filenames associated with the prospect",
        example=["doc1.pdf", "doc2.pdf"],
    )
    created_at: int = Field(
        description="Timestamp when the prospect was created", example=1622547800
    )
    updated_at: int = Field(
        description="Timestamp when the prospect was last updated", example=1622547900
    )

    class Config:
        from_attributes = True


class ProspectPut(BaseModel):
    first_name: str = Field(min_length=2, example="John")
    last_name: str = Field(min_length=2, example="Doe")


class AdvisorDisplay(BaseModel):
    id: int = Field(description="ID of the advisor", example=1)
    first_name: str = Field(description="First name of the advisor", example="Jane")
    last_name: str = Field(description="Last name of the advisor", example="Doe")
    created_at: int = Field(
        description="Unix timestamp when the advisor was created", example=1622547800
    )

    class Config:
        from_attributes = True


class AdvisorDetailDisplay(BaseModel):
    id: int = Field(description="ID of the advisor", example=1)
    first_name: str = Field(description="First name of the advisor", example="Jane")
    last_name: str = Field(description="Last name of the advisor", example="Doe")
    created_at: int = Field(
        description="Unix timestamp when the advisor was created", example=1622547800
    )
    prospects: List[ProspectDisplay] = Field(
        description="List of prospects associated with the advisor"
    )

    class Config:
        from_attributes = True


class HoldingDisplay(BaseModel):
    id: int
    symbol: Optional[str]
    description: str
    quantity: Optional[float]
    market_value: float
    currency: str

    class Config:
        from_attributes = True


class AccountListDisplay(BaseModel):
    id: int
    account_number: str
    account_type: AccountType
    currency: str
    institution: str
    created_at: int

    class Config:
        from_attributes = True


class AccountDetailDisplay(BaseModel):
    id: int
    account_number: str
    account_type: AccountType
    currency: str
    institution: str
    created_at: int
    holdings: List[HoldingDisplay]

    class Config:
        from_attributes = True


class AccountUpdate(BaseModel):
    account_type: Optional[AccountType]
    currency: Optional[str]
    institution: Optional[str]


# Add these new schemas to the existing file


class AddressPut(BaseModel):
    unit_number: Optional[str] = Field(
        None, description="Unit number of the address", example="Suite 200"
    )
    street_number: str = Field(
        ..., description="Street number of the address", example="123"
    )
    street_name: str = Field(
        ..., description="Street name of the address", example="Main Street"
    )
    city: str = Field(..., description="City of the address", example="Toronto")
    state: str = Field(
        ..., description="State or province of the address", example="Ontario"
    )
    postal_code: str = Field(
        ..., description="Postal code of the address", example="M5V 2T6"
    )
    country: str = Field(..., description="Country of the address", example="Canada")
    prospect_id: int = Field(
        ..., description="ID of the prospect associated with this address", example=1
    )


class AddressDisplay(AddressPut):
    id: int = Field(..., description="Unique identifier for the address")
    created_at: int = Field(..., description="Timestamp when the address was created")
    updated_at: int = Field(
        ..., description="Timestamp when the address was last updated"
    )

    class Config:
        from_attributes = True


# Remove the AddressCreate and AddressUpdate classes

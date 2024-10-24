from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from app.models.enums import AccountType
from app.models.schemas.holding_schema import HoldingCreateSchema, HoldingDisplaySchema


class AccountBaseSchema(BaseModel):
    account_id: Optional[str] = Field(
        description="ID of the account", example="ACC123"
    )
    account_type: AccountType = Field(
        description="Type of the account", example=AccountType.TFSA
    )
    currency: Optional[str] = Field(
        description="Currency of the account", example="CAD"
    )
    institution: Optional[str] = Field(
        description="Institution of the account", example="Bank of Canada"
    )
    management_fee_amount: Optional[float] = Field(
        description="Management fee amount for the account", example=15.00
    )
    account_value: Optional[float] = Field(
        description="Total value of the account", example=1050.50
    )


class AccountCreateSchema(AccountBaseSchema):
    holdings: List[HoldingCreateSchema] = Field(
        description="List of holdings in the account",
        example=[{"symbol": "AAPL", "quantity": 10, "market_value": 1500.00}],
    )

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
                    f"""Account value ({account_value}) does not match the sum of
                    holdings market values ({total_holdings_value})"""
                )

        return account_value


class AccountDisplaySchema(AccountBaseSchema):
    id: int = Field(description="Unique identifier for the account", example=1)
    created_at: int = Field(
        description="Timestamp when the account was created", example=1622547800
    )

    class Config:
        from_attributes = True


class AccountDetailDisplaySchema(AccountDisplaySchema):
    holdings: List[HoldingDisplaySchema] = Field(
        description="List of holdings in the account",
        example=[{"symbol": "AAPL", "quantity": 10, "market_value": 1500.00}],
    )

    class Config:
        from_attributes = True


class AccountUpdateSchema(BaseModel):
    account_id: Optional[str] = Field(
        description="ID of the account", example="ACC123"
    )
    account_type: Optional[AccountType] = Field(
        description="Type of the account", example="Savings"
    )
    currency: Optional[str] = Field(
        description="Currency of the account", example="CAD"
    )
    institution: Optional[str] = Field(
        description="Institution of the account", example="Bank of Canada"
    )

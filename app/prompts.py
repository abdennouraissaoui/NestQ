from typing import List, Optional
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator
from enum import Enum


class AccountType(str, Enum):
    TFSA = "TFSA"
    FHSA = "FHSA"
    Cash = "Cash"
    RRSP = "RRSP"
    RRSP_Spousal = "RRSP-Spousal"
    LIRA = "LIRA"
    RESP_Family = "RESP-Family"
    RIF_Spousal = "RIF-Spousal"
    RESP_Single = "RESP-Single"
    RRIF = "RRIF"
    GRSP = "GRSP"
    LRSP = "LRSP"
    LIF = "LIF"
    PRIF = "PRIF"
    GTFSA = "GTFSA"
    LRIF = "LRIF"
    RLIF = "RLIF"
    GSRSP = "GSRSP"


class Client(BaseModel):
    first_name: Optional[str] = Field(description="First name of the client")
    last_name: Optional[str] = Field(description="Last name of the client")
    client_unit_number: Optional[str] = Field(description="Unit number of the client's address")
    client_street_number: Optional[str] = Field(description="Street number of the client's address")
    client_street_name: Optional[str] = Field(description="Street name of the client's address")
    client_city: Optional[str] = Field(description="City of the client's address")
    client_province: Optional[str] = Field(description="Province of the client's address")
    client_postal_code: Optional[str] = Field(description="Postal code of the client's address")
    client_country: Optional[str] = Field(description="Country of the client's address")


class Holding(BaseModel):
    symbol: Optional[str] = Field(description="Symbol or ticker of the investment")
    description: str = Field(description="Description or name of the investment")
    cusip: Optional[str] = Field(description="CUSIP of the investment")
    quantity: Optional[float] = Field(description="Quantity of the investment.")
    book_value: Optional[float] = Field(description="Book value or cost basis of the investment")
    cost_per_share: Optional[float] = Field(description="Cost per share of the investment")
    market_value: float = Field(description="Market value of the investment")
    current_price: Optional[float] = Field(description="Current price of the investment")
    currency: str = Field(description="Currency of the holding")


class Account(BaseModel):
    account_id: Optional[str] = Field(description="ID of the account")
    account_type: AccountType = Field(description="Type of the account")
    account_value: Optional[float] = Field(description="Total value of the account")
    cash_balance: Optional[float] = Field(description="Cash balance in the account")
    statement_start_date: Optional[str] = Field(description="Statement start date for the account")
    statement_end_date: Optional[str] = Field(description="Statement end date for the account")
    management_fee_amount: Optional[float] = Field(description="Management fee amount for the account")
    holdings: List[Holding] = Field(description="List of holdings in the account")

    # @model_validator
    # def validate_account(cls, values):
    #     cash_balance = values.get('cash_balance')
    #     holdings = values.get('holdings')
    #     account_value = values.get('account_value')
    #     if cash_balance is not None and holdings is not None:
    #         total_holdings_value = sum(holding.market_value for holding in holdings)
    #         if account_value != cash_balance + total_holdings_value:
    #             raise ValueError('account_value must equal cash_balance plus sum of market value of holdings')
    #     return values


class FinancialStatement(BaseModel):
    client: Client = Field(description="Client information")
    accounts: List[Account] = Field(description="List of accounts")


INVESTMENT_STATEMENT_DATA_EXTRACTION = {
    'system': """You are an expert at extracting structured data from unstructured text. 
    
    You will ensure that the extracted data is accurate. If any information is missing from the statement, represent it as an empty string or zero, as appropriate for the data type.

    Note: The sum of the account holdings' market value and cash balance must equal the account value.
    """,
    'user': 'STATEMENT TEXT: \"\"\"{statement_text}\"\"\"'
}

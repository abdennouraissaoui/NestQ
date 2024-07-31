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
    quantity: Optional[float] = Field(description="Quantity of the investment.")
    symbol: Optional[str] = Field(description="Symbol or ticker of the investment")
    cusip: Optional[str] = Field(description="CUSIP of the investment")
    book_value: Optional[float] = Field(description="Book value or cost basis of the investment")
    cost_per_share: Optional[float] = Field(description="Cost per share of the investment")
    market_value: float = Field(description="Market value of the investment")
    current_price: Optional[float] = Field(description="Current price of the investment")
    description: str = Field(description="Description or name of the investment")
    currency: str = Field(description="Currency of the holding")


class Account(BaseModel):
    statement_start_date: Optional[str] = Field(description="Statement start date for the account")
    statement_end_date: Optional[str] = Field(description="Statement end date for the account")
    account_type: AccountType = Field(description="Type of the account")
    account_id: Optional[str] = Field(description="ID of the account")
    account_value: Optional[float] = Field(description="Total value of the account")
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

    The cash balance(s) in the account must be included with the other holdings. For cash, you only need to report the amount (market value) and the currency.""",
    'user': 'STATEMENT TEXT: \"\"\"{statement_text}\"\"\"'
}

sample_output = {'client': {'first_name': 'BLAIR STUART', 'last_name': 'MCREYNOLDS', 'address': '61 SOVEREIGN DR ST CATHARINES ON L2T 1Z6'}, 'accounts': [{'statement_start_date': 'July 31, 2022', 'statement_end_date': 'August 31, 2022', 'account_type': 'CAD LIRA', 'account_id': '3C8B0M-N', 'account_value': 568576.48, 'management_fee_amount': 422.78, 'holdings': [{'quantity': 172.0, 'symbol': 'ARKK', 'cusip': '', 'book_value': 31469.38, 'cost_per_share': 182.962, 'description': 'ARK ETF TRUST ARK INNOVATION ETF'}, {'quantity': 2389.0, 'symbol': 'XSP', 'cusip': '', 'book_value': 104447.08, 'cost_pe r_share': 43.72, 'description': 'ISHARES CORE S&P 500 INDXETF(CAD-HEDGED)'}, {'quantity': 114.0, 'symbol': 'NVDA', 'cusip': '', 'book_value': 38803.24, 'cost_per_share': 340.379, 'description': 'NVIDIA CORP'}, {'quantity': 904.425, 'symbol': 'TDB420', 'cusip': '', 'book_value': 66000.0, 'cost_per_share': 72.975, 'description': 'TD HEALTH SCIENCES FUND - F'}, {'quantity': 8776.647, 'symbol': 'NBN1033', 'cusip': '', 'book_value': 110086.37, 'cost_per_share': 12.543, 'description': 'WILLOUGHBY INVESTMENT POOL - SERIES F'}, {'quantity': 8390.303, 'symbol': 'NBN1291', 'cusip': '', 'book_value': 84607.81, 'cost_per_share': 10.084, 'description': 'FORSYTH PRIVATE REAL ESTATE PORTFOLIOS - SERIES F'}, {'quantity': 6079.499, 'symbol': 'NBN1431', 'cusip': '', 'book_value': 62353.78, 'cost_per_share': 10.256, 'description': 'LAURIER PRIVATE EQUITY POOL CLASS F'}, {'quantity': 2426.926, 'symbol': 'NBN1251B', 'cusip': '', 'book_value': 25589.02, 'cost_per_share': 10.544, 'description': 'ROCKRIDGE PRIVATE DEBT POOL SERIES BFI-F'}, {'quantity': 9453.622, 'symbol': 'NBN1251', 'cusip': '', 'book_value': 99529.63, 'cost_per_share': 10.528, 'description': 'ROCKRIDGE PRIVATE DEBT POOL SERIES F'}]}]}


data = {
    "client": {
        "first_name": "John",
        "last_name": "Doe",
        "client_unit_number": "12B",
        "client_street_number": "123",
        "client_street_name": "Main St",
        "client_city": "Toronto",
        "client_province": "ON",
        "client_postal_code": "M1A 1A1",
        "client_country": "Canada",
    },
    "accounts": [
        {
            "statement_start_date": "2024-01-01",
            "statement_end_date": "2024-06-30",
            "account_type": "TFSA",
            "account_currency": "CAD",
            "account_id": "12345678",
            "account_value": 10000.0,
            "management_fee_amount": 100.0,
            "cash_balance": 2000.0,
            "holdings": [
                {
                    "quantity": 10.0,
                    "symbol": "AAPL",
                    "cusip": "037833100",
                    "book_value": 5000.0,
                    "cost_per_share": 500.0,
                    "market_value": 8000.0,
                    "current_price": 800.0,
                    "description": "Apple Inc.",
                    "currency": "USD"
                },
                {
                    "quantity": 15.0,
                    "symbol": None,
                    "cusip": "656565",
                    "book_value": 2520.0,
                    "cost_per_share": 15.0,
                    "market_value": 457.0,
                    "current_price": '5',
                    "description": "Apple Inc.",
                    "currency": "USD"
                }
            ]
        }
    ]
}

try:
    financial_statement = FinancialStatement(**data)
    # print(financial_statement)
except ValidationError as e:
    print(e.json())


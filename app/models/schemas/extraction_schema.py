from app.models.schemas.account_schema import AccountCreateSchema
from pydantic import BaseModel, Field


class ScanExtractedDataSchema(BaseModel):
    statement_date: int = Field(
        description="The statment period end date"
    )
    investor_first_name: str = Field(
        description="First name of the investor"
    )
    investor_last_name: str = Field(
        description="Last name of the investor"
    )
    accounts: list[AccountCreateSchema]

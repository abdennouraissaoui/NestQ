from typing import List, Optional
from pydantic import BaseModel, Field, computed_field
from app.models.enums import ScanStatus
from app.models.schemas.account_schema import AccountDisplaySchema, AccountDetailDisplaySchema
from app.models.schemas.prospect_schema import ProspectDisplaySchema


class ScanDisplaySchema(BaseModel):
    id: int = Field(description="ID of the scan", example=1)
    prospect_id: int = Field(
        description="ID of the prospect associated with the scan",
        example=1
    )
    file_name: str = Field(description="Name of the file", example="scan.pdf")
    status: ScanStatus = Field(
        description="Current status of the scan", example="completed"
    )
    created_at: int = Field(
        description="Timestamp when the scan was created",
        example=1672537600,
    )
    updated_at: int = Field(
        description="Timestamp when the scan was last updated",
        example=1672540800,
    )

    statement_date: int = Field(
        description="Date of the statement in format YYYYMMDD",
        example=20240830,
    )

    accounts: List[AccountDisplaySchema] = Field(
        description="List of accounts associated with the scan"
    )

    prospect: ProspectDisplaySchema = Field(
        description="Prospect associated with the scan"
    )

    @computed_field
    def investor_first_name(self) -> str:
        return self.prospect.first_name

    @computed_field
    def investor_last_name(self) -> str:
        return self.prospect.last_name

    @computed_field
    def amount(self) -> float:
        return sum(account.account_value or 0 for account in self.accounts)

    @computed_field
    def institution(self) -> str:
        return ', '.join(set(account.institution for account in self.accounts if account.institution))

    class Config:
        from_attributes = True


class ScanDisplayDetailSchema(ScanDisplaySchema):
    accounts: List[AccountDetailDisplaySchema] = Field(
        description="List of accounts associated with the scan"
    )

    class Config:
        from_attributes = True


class ScanProcessorUpdateSchema(BaseModel):
    prospect_id: Optional[int] = Field(default=None, description="ID of the prospect", example=1)
    status: Optional[ScanStatus] = Field(
        default=None,
        description="Updated status of the scan",
        example="processing"
    )
    processing_time: Optional[float] = Field(
        default=None,
        description="Time taken to process the scan in seconds",
        example=10.0
    )
    page_count: Optional[int] = Field(
        default=None,
        description="Number of pages scanned",
        example=5
    )
    ocr_source: Optional[str] = Field(
        default=None,
        description="Source of the OCR data",
        example="OCR Engine 1"
    )
    llm_source: Optional[str] = Field(
        default=None,
        description="Source of the LLM data",
        example="LLM Engine 1"
    )
    ocr_text: Optional[str] = Field(
        default=None,
        description="Text extracted from the OCR data",
        example="OCR Text"
    )
    ocr_text_cleaned: Optional[str] = Field(
        default=None,
        description="Cleaned text extracted from the OCR data",
        example="Cleaned OCR Text"
    )
    statement_date: Optional[int] = Field(
        default=None,
        description="Timestamp when the statement was created"
    )


class ScanCreateSchema(ScanProcessorUpdateSchema):
    file_name: str = Field(description="Name of the uploaded file", example="statement.pdf")
    uploaded_file: bytes = Field(description="Base64 encoded content of the uploaded file")

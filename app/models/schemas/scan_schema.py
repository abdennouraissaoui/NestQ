from typing import List, Optional
from pydantic import BaseModel, Field, computed_field
from app.models.enums import ScanStatus
from app.models.schemas.account_schema import (
    AccountDisplaySchema,
    AccountDetailDisplaySchema,
)
from app.models.schemas.prospect_schema import ProspectDisplaySchema


class FileUploadSchema(BaseModel):
    file_name: str = Field(description="Name of the file", example="scan.pdf")
    id: int = Field(description="ID of the scan", example=1)
    status: ScanStatus = Field(
        description="Current status of the scan", example="completed"
    )

    prospect: Optional[ProspectDisplaySchema] = Field(
        default=None, description="Prospect associated with the scan", exclude=True
    )

    prospect_id: Optional[int] = Field(
        default=None,
        description="ID of the prospect associated with the scan",
        example=1,
    )

    @computed_field
    def investor_first_name(self) -> Optional[str]:
        return self.prospect.first_name if self.prospect else None

    @computed_field
    def investor_last_name(self) -> Optional[str]:
        return self.prospect.last_name if self.prospect else None

    created_at: int = Field(
        description="Timestamp when the scan was created",
        example=1672537600,
    )
    updated_at: int = Field(
        description="Timestamp when the scan was last updated",
        example=1672540800,
    )

    class Config:
        from_attributes = True


class ScanDisplaySchema(FileUploadSchema):
    accounts: List[AccountDisplaySchema] = Field(
        default_factory=list,
        description="List of accounts associated with the scan",
    )

    statement_date: Optional[int] = Field(
        default=None,
        description="Date of the statement in format YYYYMMDD",
        example=20240830,
    )

    @computed_field
    def amount(self) -> float:
        """Total value of all accounts in the scan"""
        return sum(account.account_value or 0 for account in self.accounts)

    @computed_field
    def institution(self) -> str:
        """Comma-separated list of unique institutions in the scan"""
        return ", ".join(
            sorted(
                set(
                    account.institution
                    for account in self.accounts
                    if account.institution
                )
            )
        )

    class Config:
        from_attributes = True


class ScanDisplayDetailSchema(ScanDisplaySchema):
    accounts: List[AccountDetailDisplaySchema] = Field(
        description="Detailed list of accounts associated with the scan"
    )

    class Config:
        from_attributes = True


class OcrResultSchema(BaseModel):
    scan_id: int = Field(description="ID of the scan", example=1)
    ocr_source: Optional[str] = Field(
        default=None, description="Source of the OCR data", example="OCR Engine 1"
    )
    llm_source: Optional[str] = Field(
        default=None, description="Source of the LLM data", example="LLM Engine 1"
    )
    error_message: Optional[str] = Field(
        default=None, description="Error message if the OCR failed"
    )
    ocr_text: Optional[str] = Field(
        default=None, description="Raw OCR text", example="Raw OCR text"
    )
    ocr_text_cleaned: Optional[str] = Field(
        default=None, description="Cleaned OCR text", example="Cleaned OCR text"
    )
    processing_time: Optional[float] = Field(
        default=None, description="Processing time in seconds", example=1.5
    )
    statement_date: Optional[int] = Field(
        default=None,
        description="Date of the statement in format YYYYMMDD",
        example=20240830,
    )

    class Config:
        from_attributes = True


class ScanProcessorUpdateSchema(BaseModel):
    prospect_id: Optional[int] = Field(
        default=None, description="ID of the prospect", example=1
    )
    status: Optional[ScanStatus] = Field(
        default=None,
        description="Updated status of the scan",
        example="processing",
    )

    class Config:
        from_attributes = True


class ScanCreateSchema(BaseModel):
    prospect_id: int = Field(description="ID of the prospect", example=1)
    file_name: str = Field(
        description="Name of the uploaded file", example="statement.pdf"
    )
    blob_name: str = Field(
        description="Name of the blob in the cloud storage",
        example="statement.pdf",
    )
    status: ScanStatus = Field(
        description="Current status of the scan", example="processing"
    )

    class Config:
        from_attributes = True

from typing import List
from pydantic import BaseModel, Field
from app.models.enums import ScanStatus
from app.models.schemas.account_schema import (
    AccountCreateSchema,
    AccountDisplaySchema,
)


class ScanCreateSchema(BaseModel):
    prospect_id: int = Field(description="ID of the prospect", example=1)


class ScanDisplaySchema(BaseModel):
    id: int = Field(description="ID of the scan", example=1)
    prospect_id: int = Field(
        description="ID of the prospect associated with the scan", example=1
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

    class Config:
        from_attributes = True


class ScanDisplayDetailSchema(ScanDisplaySchema):
    accounts: List[AccountDisplaySchema] = Field(
        description="List of accounts associated with the scan"
    )


class ScanProcessorUpdateSchema(BaseModel):
    status: ScanStatus = Field(
        description="Updated status of the scan", example="processing"
    )
    processing_time: float = Field(
        description="Time taken to process the scan in seconds", example=10.0
    )
    page_count: int = Field(description="Number of pages scanned", example=5)
    ocr_source: str = Field(
        description="Source of the OCR data", example="OCR Engine 1"
    )
    llm_source: str = Field(
        description="Source of the LLM data", example="LLM Engine 1"
    )


class ScanExtractedDataSchema(BaseModel):
    accounts: list[AccountCreateSchema]

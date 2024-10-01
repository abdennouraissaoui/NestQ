"""

Orchestrates the extraction of holdings from a financial statement.
"""

from app.services.prompts import INVESTMENT_STATEMENT_DATA_EXTRACTION

from app.models.schemas.scan_schema import ScanExtractedDataSchema

from app.services.llm_factory import LlmFactory

from app.services.ocr_service import OcrFactory

from app.services.text_cleanup import (
    remove_disclaimer_pages,
    clean_markdown_text,
    remove_informational_text,
)

from typing import Tuple

from app.models.schemas.scan_schema import ScanProcessorUpdateSchema

from app.models.enums import ScanStatus
import time


class FinancialStatementProcessor:
    def __init__(
        self,
        ocr_provider: str = "document-intelligence",
        llm_provider: str = "azure-openai",
    ):
        self.ocr_factory = OcrFactory(ocr_provider)

        self.llm_factory = LlmFactory(llm_provider)

    def process_scan(
        self, file_base64: str
    ) -> Tuple[ScanProcessorUpdateSchema, ScanExtractedDataSchema]:
        start_time = time.time()

        cleaned_doc_base64 = remove_disclaimer_pages(file_base64)

        ocr_result = self.ocr_factory.get_document_analysis(cleaned_doc_base64)

        markdown_text = clean_markdown_text(ocr_result.content)

        context: str = remove_informational_text(markdown_text)

        # Extract statement information only once

        extracted_data: ScanExtractedDataSchema = self.extract_financial_statement(
            context
        )

        scan_update = ScanProcessorUpdateSchema(
            ocr_text=markdown_text,
            ocr_text_cleaned=context,
            processing_time=float(time.time() - start_time),
            status=ScanStatus.PROCESSED,
            page_count=len(ocr_result.pages),
            ocr_source=self.ocr_factory.provider,
            llm_source=self.llm_factory.provider,
        )

        return scan_update, extracted_data

    def extract_financial_statement(self, context: str) -> ScanExtractedDataSchema:
        messages = [
            {
                "role": "system",
                "content": INVESTMENT_STATEMENT_DATA_EXTRACTION["system"],
            },
            {
                "role": "user",
                "content": INVESTMENT_STATEMENT_DATA_EXTRACTION["user"].format(
                    statement_text=context
                ),
            },
        ]

        completion = self.llm_factory.create_completion(
            model="gpt-4o",
            response_format=ScanExtractedDataSchema,
            messages=messages,
        )

        return completion.choices[0].message.parsed


# Example usage

if __name__ == "__main__":
    extractor = FinancialStatementProcessor()

    financial_statement = extractor.extract_financial_statement()

    print(financial_statement)

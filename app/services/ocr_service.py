from azure.core.exceptions import HttpResponseError
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import (
    AnalyzeDocumentRequest,
    ContentFormat,
    AnalyzeResult,
)
from app.config import app_config
from typing import Any


class OcrFactory:
    def __init__(self, provider: str):
        self.provider = provider
        self.client = self._initialize_client()

    def _initialize_client(self) -> Any:
        assert self.provider in ["document-intelligence"]
        if self.provider == "document-intelligence":
            return DocumentIntelligenceClient(
                endpoint=app_config.DOC_INTEL_ENDPOINT,
                credential=AzureKeyCredential(app_config.DOC_INTEL_API_KEY),
            )

    def get_document_analysis(self, file_base64: str) -> AnalyzeResult:
        poller = self.client.begin_analyze_document(
            "prebuilt-layout",
            AnalyzeDocumentRequest(bytes_source=file_base64),
            locale="en-US",
            output_content_format=ContentFormat.MARKDOWN,
        )
        try:
            result: AnalyzeResult = poller.result()
        except HttpResponseError as error:
            if error.error is not None:
                if error.error.code == "InvalidImage":
                    print(f"Received an invalid image error: {error.error}")
                if error.error.code == "InvalidRequest":
                    print(f"Received an invalid request error: {error.error}")
                raise
            if "Invalid request".casefold() in error.message.casefold():
                print(f"Uh-oh! Seems there was an invalid request: {error}")
            raise
        return result


if __name__ == "__main__":
    from app.utils.utility import load_file_as_base64

    # Initialize the OcrFactory with the document-intelligence provider
    ocr_factory = OcrFactory("document-intelligence")

    # Load a sample PDF file as base64
    sample_file_path = "./data/sample_statements/IG.pdf"
    sample_base64 = load_file_as_base64(sample_file_path)

    # Get document analysis
    result = ocr_factory.get_document_analysis(sample_base64)

    # Process the result
    print("Document analysis completed successfully.")
    print(f"Number of pages: {len(result.pages)}")
    print(
        f"Content: {result.content[:500]}..."
    )  # Print first 500 characters of content

    # You can further process the result as needed
    # For example, extracting text from specific regions, tables, etc.
    if result.tables:
        print(f"Number of tables detected: {len(result.tables)}")
        for i, table in enumerate(result.tables):
            print(
                f"Table {i+1} dimensions: {table.row_count} rows x {table.column_count} columns"
            )

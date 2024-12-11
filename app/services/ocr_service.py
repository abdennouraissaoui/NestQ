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
import pandas as pd
from functools import partial
import asyncio


def table_to_dataframe(table_data):
    """
    Convert table data structure to pandas DataFrame.

    Args:
        table_data (dict): Dictionary containing table information with 'cells' list

    Returns:
        pd.DataFrame: Processed table data as a DataFrame
    """
    # Get number of rows and columns
    num_rows = table_data["rowCount"]
    num_cols = table_data["columnCount"]

    # Initialize empty 2D list to store data
    data = [["" for _ in range(num_cols)] for _ in range(num_rows)]

    # Fill in the data
    for cell in table_data["cells"]:
        row_idx = cell["rowIndex"]
        col_idx = cell["columnIndex"]
        content = cell["content"].strip()
        # Remove the bullet point if present
        if content.startswith("·"):
            content = content[1:].strip()
        data[row_idx][col_idx] = content

    # Create DataFrame
    df = pd.DataFrame(data)

    return df


def doc_intel_to_df(result: AnalyzeResult) -> list[pd.DataFrame]:
    """
    Converts Document Intelligence tables to pandas DataFrames

    Args:
        result: The AnalyzeResult from Document Intelligence

    Returns:
        List of pandas DataFrames, one for each table in the document
    """
    df_list = []
    for table in result.tables:
        df = table_to_dataframe(table)
        df_list.append(df)
    return df_list


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

    async def get_document_analysis(self, file_base64: str) -> AnalyzeResult:
        # Run the blocking operations in a thread pool
        loop = asyncio.get_running_loop()
        try:
            # Run begin_analyze_document in thread pool
            poller = await loop.run_in_executor(
                None,
                partial(
                    self.client.begin_analyze_document,
                    "prebuilt-layout",
                    AnalyzeDocumentRequest(bytes_source=file_base64),
                    locale="en-US",
                    output_content_format=ContentFormat.MARKDOWN,
                ),
            )

            # Run poller.result() in thread pool
            result: AnalyzeResult = await loop.run_in_executor(None, poller.result)

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
    import base64

    ocr_factory = OcrFactory("document-intelligence")

    # Load a sample PDF file as base64
    sample_file_path = (
        r"C:\Users\abden\Desktop\pdf_report_P_1515740_12-10-2024_lmqxH9t.pdf"
    )
    with open(sample_file_path, "rb") as file:
        sample_base64 = base64.b64encode(file.read()).decode("utf-8")

    result = asyncio.run(ocr_factory.get_document_analysis(sample_base64))

    print("Document analysis completed successfully.")
    print(f"Number of pages: {len(result.pages)}")
    print(
        f"Content: {result.content[:500]}..."
    )  # Print first 500 characters of content

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
                f"Table {i + 1} dimensions: {table.row_count} rows x {table.column_count} columns"
            )

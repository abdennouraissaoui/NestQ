"""
Logic for interacting with the OCR service
"""

from azure.core.exceptions import HttpResponseError

from app.utils.utility import get_client
from azure.ai.documentintelligence.models import (
    AnalyzeDocumentRequest,
    ContentFormat,
    AnalyzeResult,
)


def get_document_analysis(file_base64) -> AnalyzeResult:
    document_ai_client = get_client("document-intelligence")
    poller = document_ai_client.begin_analyze_document(
        "prebuilt-layout",
        AnalyzeDocumentRequest(bytes_source=file_base64),
        locale="en-US",
        output_content_format=ContentFormat.MARKDOWN,
    )
    try:
        result: AnalyzeResult = poller.result()
    except HttpResponseError as error:
        # Examples of how to check an HttpResponseError
        # Check by error code:
        if error.error is not None:
            if error.error.code == "InvalidImage":
                print(f"Received an invalid image error: {error.error}")
            if error.error.code == "InvalidRequest":
                print(f"Received an invalid request error: {error.error}")
            # Raise the error again after printing it
            raise
        # If the inner error is None and then it is possible to check the message to get more information:
        if "Invalid request".casefold() in error.message.casefold():
            print(f"Uh-oh! Seems there was an invalid request: {error}")
        # Raise the error again
        raise
    return result

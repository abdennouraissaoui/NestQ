"""
Orchestration of the text cleanup process
"""

from app.services.text_cleanup.feature_extraction import (
    PageFeatureExtractor,
    LineFeatureExtractor,
)
from app.services.ocr_service import get_document_analysis
from app.services.text_cleanup.classifier import classify_relevance
import fitz
import base64
from io import BytesIO


def get_llm_ready_text(input_file_path: str) -> str:
    """
    Extracts relevant text from a statement and returns a string that is ready for an LLM.
    """
    # Remove disclaimer pages from the input file (if they exist)
    cleaned_doc_base64 = remove_disclaimer_pages(input_file_path)

    # Get the markdown formatted text from the document
    markdown_text = get_document_analysis(cleaned_doc_base64)

    # clean up the markdown formatted text by removing the standard disclaimer texts
    context: str = remove_informational_text(markdown_text)

    return context


def remove_disclaimer_pages(input_file_path: str) -> str:
    """
    Remove disclaimer pages from the input file (if they exist)
    """
    page_feature_extractor = PageFeatureExtractor()

    # Open the PDF file
    pdf = fitz.open(input_file_path)

    # Create a new PDF to store relevant pages
    new_pdf = fitz.open()

    for page in pdf:
        # Extract text from the page
        page_text = page.get_text()

        # Extract features and classify relevance
        features = page_feature_extractor.extract_features(page_text)
        is_relevant = classify_relevance(features)

        if is_relevant:
            new_pdf.insert_pdf(pdf, from_page=page.number, to_page=page.number)

    # Convert the new PDF to base64
    buffer = BytesIO()
    new_pdf.save(buffer)
    pdf_bytes = buffer.getvalue()
    base64_pdf = base64.b64encode(pdf_bytes).decode()

    # Close both PDFs
    pdf.close()
    new_pdf.close()

    return base64_pdf


def remove_informational_text(markdown_text: str) -> str:
    """
    Remove the standard informational text from the markdown text
    """
    line_feature_extractor = LineFeatureExtractor()

    # Split the markdown text into lines
    lines = markdown_text.split("\n")

    # Create a new list to store relevant lines
    relevant_lines = []

    for line in lines:
        features = line_feature_extractor.extract_features(line)
        is_relevant = classify_relevance(features)

        if is_relevant:
            relevant_lines.append(line)

    # Join the relevant lines back into a single string
    cleaned_text = "\n".join(relevant_lines)

    return cleaned_text


if __name__ == "__main__":
    print(get_llm_ready_text("data/sample_statements/10-K/0000320193-23-000060.pdf"))

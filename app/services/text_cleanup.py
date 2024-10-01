"""
Orchestration of the text cleanup process
"""

from model.feature_extraction import (
    PageFeatureExtractor,
    ExcerptFeatureExtractor,
)
from app.services.ocr_service import OcrFactory
import fitz
import base64
from io import BytesIO
import joblib

# from app.config import Config
from utils.utility import clean_markdown_text


class StatementExcerptClassifier:
    """
    Classifier for statement excerpts or pages.
    """

    def __init__(self, classification_level):
        assert classification_level in [
            "page",
            "excerpt",
        ], "Classification level must be either 'page' or 'excerpt'"
        if classification_level == "page":
            self.classifier = joblib.load("./page_relevance_classifier.joblib")
            self.feature_extractor = PageFeatureExtractor()
        elif classification_level == "excerpt":
            self.classifier = joblib.load("./excerpt_relevance_classifier.joblib")
            self.feature_extractor = ExcerptFeatureExtractor()
        self.items_loaded: bool = False

    def load_document_items(self, items: list[str]):
        """
        Load the document items into the feature extractor.
        """
        for item in items:
            self.feature_extractor.add(item)
        self.items_loaded = True

    def get_relevant_items_index(self) -> list[int]:
        """
        Returns index of relevant items.
        """
        if not self.items_loaded:
            raise ValueError("No items loaded")

        features = self.feature_extractor.extract_document_features()
        predictions = self.classifier.predict(features)
        excluded_indices = [i for i, pred in enumerate(predictions) if pred == 1]
        relevant_indices = [
            i for i in range(len(predictions)) if i not in excluded_indices
        ]
        # TODO: Use a model with predict_proba to get the threshold
        return relevant_indices
        # relevant_indices = [
        #     i
        #     for i, prob in enumerate(probabilities)
        #     if prob > Config.RELEVANCE_THRESHOLD
        # ]

        return relevant_indices


def remove_informational_text(markdown_text: str) -> str:
    """
    Remove the standard informational text from the markdown text
    """
    classifier = StatementExcerptClassifier(classification_level="excerpt")

    # Split the markdown text into paragraphs
    paragraphs = markdown_text.split("\n\n")

    # Load paragraphs into the classifier
    classifier.load_document_items(paragraphs)

    # Get relevant paragraph indices
    relevant_indices = classifier.get_relevant_items_index()

    # Keep only the relevant paragraphs
    relevant_paragraphs = [paragraphs[i] for i in relevant_indices]

    # Join the relevant paragraphs back into a single string
    cleaned_text = "\n\n".join(relevant_paragraphs)

    return cleaned_text


def remove_disclaimer_pages(input_base64: str) -> str:
    """
    Remove disclaimer pages from the input base64-encoded PDF (if they exist)
    """
    classifier = StatementExcerptClassifier(classification_level="page")

    # Decode base64 to PDF bytes
    pdf_bytes = base64.b64decode(input_base64)

    # Open the PDF from bytes
    pdf = fitz.open(stream=pdf_bytes, filetype="pdf")

    # Create a new PDF to store relevant pages
    new_pdf = fitz.open()
    pages_str = [page.get_text() for page in pdf]
    classifier.load_document_items(pages_str)
    relevant_pages = classifier.get_relevant_items_index()
    for i in relevant_pages:
        new_pdf.insert_pdf(pdf, from_page=i, to_page=i)

    # Convert the new PDF to base64
    buffer = BytesIO()
    new_pdf.save(buffer)
    new_pdf_bytes = buffer.getvalue()
    base64_pdf = base64.b64encode(new_pdf_bytes).decode()

    # Close both PDFs
    pdf.close()
    new_pdf.close()

    return base64_pdf


# def get_llm_ready_text(input_base64: str) -> str:
#     """
#     Extracts relevant text from a statement and returns a string that is ready for an LLM.
#     """
#     # Remove disclaimer pages from the input file (if they exist)
#     cleaned_doc_base64 = remove_disclaimer_pages(input_base64)

#     # Get the markdown formatted text from the document
#     ocr_factory = OcrFactory("document-intelligence")
#     result = ocr_factory.get_document_analysis(cleaned_doc_base64)
#     markdown_text = clean_markdown_text(result.content)

#     # clean up the markdown formatted text by removing the standard disclaimer texts
#     context: str = remove_informational_text(markdown_text)

#     return context


if __name__ == "__main__":
    from utils.utility import load_file_as_base64
    from app.services.statement_extractor import StatementExtractor
    from app.models.schemas.account_schema import AccountCreateSchema

    ocr_factory = OcrFactory("document-intelligence")
    extractor = StatementExtractor(llm_provider="azure-openai")

    file_path = "./model/data/sample_statements/CI.pdf"
    # Load the PDF file as base64
    input_base64 = load_file_as_base64(file_path)

    # Process the PDF and get LLM-ready text
    cleaned_doc_base64 = remove_disclaimer_pages(input_base64)

    # Get the markdown formatted text from the document
    result = ocr_factory.get_document_analysis(cleaned_doc_base64)
    markdown_text = clean_markdown_text(result.content)

    # clean up the markdown formatted text by removing the standard disclaimer texts
    llm_ready_text: str = remove_informational_text(markdown_text)
    accounts: list[AccountCreateSchema] = extractor.extract_financial_statement(
        llm_ready_text
    )
    # Print a preview of the result
    print("LLM-ready text preview:")
    print(
        llm_ready_text[:500] + "..."
        if len(llm_ready_text) > 500
        else llm_ready_text
    )

    # Optionally, save the result to a file
    with open("llm_ready_text.txt", "w", encoding="utf-8") as output_file:
        output_file.write(llm_ready_text)
    print("\nFull text has been saved to 'llm_ready_text.txt'")

    financial_statement = extractor.extract_financial_statement(llm_ready_text)
    print(financial_statement)

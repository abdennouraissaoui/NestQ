"""
Orchestration of the text cleanup process
"""

from app.preprocessing.feature_extraction import (
    PageFeatureExtractor,
    ExcerptFeatureExtractor,
)
import fitz
import base64
from io import BytesIO
import joblib
from app.services.exerpt_classifier import ExerptClassifier


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
            self.classifier = joblib.load("./app/services/page_relevance_classifier.joblib")
            self.feature_extractor = PageFeatureExtractor()
        elif classification_level == "excerpt":
            self.classifier = joblib.load("./app/services/excerpt_relevance_classifier.joblib")
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
    model_config = {
        'pipeline_path': "./app/services/svm_filter_pipeline.pkl"
    }
    classifier = ExerptClassifier(model_config)
    included_texts = classifier.filter_included(markdown_text.split("\n\n"))

    # Join the relevant paragraphs back into a single string
    cleaned_text = "\n\n".join(included_texts)

    return cleaned_text


def remove_disclaimer_pages(input_base64: str) -> str:
    """
    Remove disclaimer pages from the input base64-encoded PDF and return a new base64-encoded PDF.

    This function takes a base64-encoded PDF as input, processes it to identify and remove
    disclaimer pages, and returns a new base64-encoded PDF containing only the relevant pages.

    Args:
        input_base64 (str): A base64-encoded string representing the input PDF.

    Returns:
        str: A base64-encoded string representing the new PDF with disclaimer pages removed.

    Raises:
        ValueError: If the input is not a valid base64-encoded PDF.
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

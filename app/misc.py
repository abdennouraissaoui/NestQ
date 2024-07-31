from app.azure_ocr import get_document_analysis
from app.utility import load_file_as_base64, load_sample_statements_ocr, save_sample_statements_ocr
import os
from tqdm import tqdm


def find_pdfs(directory):
    """
    Find all PDF files in a given directory.

    This function recursively searches through the directory and its subdirectories for PDF files.
    """
    # Get the absolute path of the current directory
    abs_directory = os.path.abspath(directory)

    # List to store absolute paths of PDF files
    pdf_paths = []

    # Walk through the directory
    for root, _, files in os.walk(abs_directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                # Get the absolute path of the PDF file
                pdf_path = os.path.join(root, file)
                pdf_paths.append(pdf_path)

    return pdf_paths


def ocr_sample_statements(directory):
    """
    OCR all the PDF files in the given directory and save the results to a pickle file.

    The pickle file will be named "sample_statements_ocr.pkl" and will contain a dictionary with the file names as keys
     and the OCR results as values.

    """
    pdf_paths = find_pdfs(directory)
    scanned_pdfs = load_sample_statements_ocr()
    for pdf_path in tqdm(pdf_paths):
        file_name = pdf_path.split("\\")[-1]
        if file_name not in scanned_pdfs:
            result = get_document_analysis(load_file_as_base64(pdf_path))
            scanned_pdfs[file_name] = result
            save_sample_statements_ocr(scanned_pdfs)


if __name__ == "__main__":
    ocr_sample_statements('../data/sample_statements')

import os
import pickle
from tqdm import tqdm
from app.services.ocr_service import OcrFactory
from app.utils.utility import load_file_as_base64


def get_processed_files(pickle_dir):
    return {
        f.replace(".pickle", "")
        for f in os.listdir(pickle_dir)
        if f.endswith(".pickle")
    }


def process_pdfs(root_dir):
    ocr = OcrFactory("document-intelligence")
    processed_files = get_processed_files(root_dir)
    total_pdfs = 0
    total_errors = 0

    for subdir, _, files in os.walk(root_dir):
        pdf_files = [f for f in files if f.lower().endswith(".pdf")]
        for file in tqdm(pdf_files, desc=f"Processing {subdir}"):
            if file in processed_files:
                continue

            total_pdfs += 1
            file_path = os.path.join(subdir, file)
            pickle_path = os.path.join(subdir, f"{file}.pickle")

            try:
                pdf_base64 = load_file_as_base64(file_path)
                result = ocr.get_document_analysis(pdf_base64)

                # Save the result immediately
                with open(pickle_path, "wb") as f:
                    pickle.dump(result, f)

                processed_files.add(file)
            except Exception as e:
                print(f"Error processing {file}: {str(e)}")
                total_errors += 1

    print(f"Total PDFs processed: {total_pdfs}")
    print(f"Number of errors encountered: {total_errors}")


if __name__ == "__main__":
    root_directory = r"G:\My Drive\Startup\NestQ\statements_clustered"
    # root_directory = r"C:\Users\abden\Desktop\NestQ\data\sample_statements\target"
    process_pdfs(root_directory)

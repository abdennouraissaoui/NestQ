import os
import pickle
from tqdm import tqdm
from app.services.ocr_service import OcrFactory
from utils.utility import load_file_as_base64, clean_markdown_text
import pandas as pd
from model.feature_extraction import StatementExcerptClassifier


def get_ocred_files(pickle_dir):
    return {
        f.replace(".pickle", "")
        for f in os.listdir(pickle_dir)
        if f.endswith(".pickle")
    }


def load_pickle_file(file_path):
    with open(file_path, "rb") as f:
        return pickle.load(f)


def get_classified_pdfs(csv_file):
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        return set(df["file_name"].unique())
    return set()


def ocr_pdfs_and_store_results(root_dir):
    ocr = OcrFactory("document-intelligence")
    ocred_files = get_ocred_files(root_dir)
    total_pdfs = 0
    total_errors = 0

    for subdir, _, files in os.walk(root_dir):
        pdf_files = [f for f in files if f.lower().endswith(".pdf")]
        for file in tqdm(pdf_files, desc=f"OCRing PDFs in {subdir}"):
            if file in ocred_files:
                continue

            total_pdfs += 1
            file_path = os.path.join(subdir, file)
            pickle_path = os.path.join(subdir, f"{file}.pickle")

            try:
                pdf_base64 = load_file_as_base64(file_path)
                result = ocr.get_document_analysis(pdf_base64)

                # Save the OCR result immediately
                with open(pickle_path, "wb") as f:
                    pickle.dump(result, f)

                ocred_files.add(file)
            except Exception as e:
                print(f"Error OCRing {file}: {str(e)}")
                total_errors += 1

    print(f"Total PDFs OCRed: {total_pdfs}")
    print(f"Number of OCR errors encountered: {total_errors}")


def classify_pdf_content(root_dir):
    gpt_classifier = StatementExcerptClassifier("azure-openai")
    llama_classifier = StatementExcerptClassifier("local-lm-studio")

    output_file = "exerpt_relevance_classification_data.csv"
    classified_pdfs = get_classified_pdfs(output_file)

    for subdir, _, files in os.walk(root_dir):
        pickle_files = [f for f in files if f.endswith(".pickle")]
        for file in pickle_files:
            if file in classified_pdfs:
                continue

            file_path = os.path.join(subdir, file)
            try:
                result = load_pickle_file(file_path)
                markdown_content = clean_markdown_text(result.content)
                lines = [
                    line.strip()
                    for line in markdown_content.split("\n\n")
                    if line.strip()
                ]

                data = []
                for line in tqdm(lines, desc=f"Classifying lines in {file}"):
                    from concurrent.futures import ThreadPoolExecutor

                    with ThreadPoolExecutor(max_workers=2) as executor:
                        gpt_future = executor.submit(
                            gpt_classifier.classify, line, "gpt-4o-mini"
                        )
                        llama_future = executor.submit(
                            llama_classifier.classify,
                            line,
                            "meta-llama-3.1-8b-instruct-q4_k_m",
                        )

                        gpt_classification = gpt_future.result()
                        llama_classification = llama_future.result()
                    char_count = len(line)
                    data.append(
                        {
                            "text": line,
                            "exclude_gpt": gpt_classification["exclude"],
                            "exclude_llama": llama_classification["exclude"],
                            "char_count": char_count,
                            "file_name": file,
                        }
                    )

                # Save progress after processing each PDF
                save_to_csv(data, output_file)
                classified_pdfs.add(file)

            except Exception as e:
                print(f"Error classifying {file}: {str(e)}")


def save_to_csv(data, output_file):
    df = pd.DataFrame(data)
    mode = "a" if os.path.exists(output_file) else "w"
    header = not os.path.exists(output_file)
    df.to_csv(output_file, mode=mode, header=header, index=False)


if __name__ == "__main__":
    # root_directory = r"G:\My Drive\Startup\NestQ\statements_clustered"
    root_directory = r"C:\Users\abden\Desktop\NestQ\data\sample_statements\target"
    ocr_pdfs_and_store_results(root_directory)
    classify_pdf_content(root_directory)

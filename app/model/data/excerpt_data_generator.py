import os
import pickle
from tqdm import tqdm
from app.services.ocr_service import OcrFactory
from app.utils.utility import load_file_as_base64, clean_markdown_text
import pandas as pd
from app.services.text_cleanup import StatementExcerptClassifier
from model.data.llm import StatementExerptClassifier


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
    gpt_classifier = StatementExerptClassifier("azure-openai")
    llama_classifier = StatementExerptClassifier("local-lm-studio")

    output_file = "excerpt_relevance_classification_data.csv"
    classified_pdfs = get_classified_pdfs(output_file)

    for subdir, _, files in os.walk(root_dir):
        pickle_files = [f for f in files if f.endswith(".pickle")]
        import random

        sample_size = min(25, len(pickle_files))
        pickle_files = random.sample(pickle_files, sample_size)
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
                    svm_classifier = StatementExcerptClassifier(
                        classification_level="excerpt"
                    )
                    svm_classifier.load_document_items([line])
                    svm_classification = svm_classifier.get_relevant_items_index()
                    svm_class = 0 if len(svm_classification) > 0 else 1

                    # from concurrent.futures import ThreadPoolExecutor

                    # with ThreadPoolExecutor(max_workers=2) as executor:
                    #     gpt_future = executor.submit(
                    #         gpt_classifier.classify, line, "gpt-4o"
                    #     )
                    #     # llama_future = executor.submit(
                    #     #     llama_classifier.classify,
                    #     #     line,
                    #     #     "llama-3.2-3b-instruct",
                    #     # )

                    #     gpt_classification = gpt_future.result()
                    #     # llama_classification = llama_future.result()
                    try:
                        gpt_classification = gpt_classifier.classify(line, "gpt-4o")
                        char_count = len(line)
                        classification = {
                            "text": line,
                            "exclude_gpt": gpt_classification[0],
                            "confidence_gpt": gpt_classification[1],
                            "exclude_llama": None,
                            "svm_class": svm_class,
                            "char_count": char_count,
                            "file_name": file,
                        }
                        data.append(classification)
                        import time
                        time.sleep(0.1)
                    except Exception as e:
                        print(f"Error classifying {line}: {str(e)}")

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
    root_directory = (
        # r"C:\Users\abden\Desktop\NestQ\model\data\sample_statements\target"
        r"G:\My Drive\Startup\NestQ\statements_clustered"
    )
    # ocr_pdfs_and_store_results(root_directory)
    classify_pdf_content(root_directory)

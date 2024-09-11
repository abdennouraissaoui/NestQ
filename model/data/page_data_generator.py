import os
import csv
import fitz
from tqdm import tqdm
from app.services.text_cleanup.text_classification.llm import DisclaimerPageClassifier
import pandas as pd


def get_processed_files(csv_file):
    processed_files = set()
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file, encoding="utf-8")
        processed_files = set(df["file_name"])
    return processed_files


def process_pdfs(root_dir):
    classifier = DisclaimerPageClassifier()
    output_file = "disclaimer_classification_data.csv"
    processed_files = get_processed_files(output_file)
    total_pdfs = 0
    total_pages = 0
    total_disclaimers = 0
    total_errors = 0
    total_skipped = 0

    mode = "a" if os.path.exists(output_file) else "w"
    with open(output_file, mode, newline="", encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile)
        if mode == "w":
            csvwriter.writerow(
                ["page_text", "label", "subdirectory_path", "file_name", "page_number"]
            )

        for subdir, _, files in os.walk(root_dir):
            for file in tqdm(files, desc=f"Processing {subdir}"):
                if file.lower().endswith(".pdf"):
                    if file in processed_files:
                        total_skipped += 1
                        continue

                    total_pdfs += 1
                    file_path = os.path.join(subdir, file)
                    try:
                        doc = fitz.open(file_path)
                        for page_num in range(len(doc)):
                            total_pages += 1
                            try:
                                page = doc[page_num]
                                text = page.get_text()
                                if not text.strip():
                                    continue
                                classification = classifier.is_disclaimer(text)
                                label = classification["is_disclaimer"]
                                if label == 1:
                                    total_disclaimers += 1
                                csvwriter.writerow(
                                    [text, label, subdir, file, page_num]
                                )
                                csvfile.flush()  # Ensure data is written immediately
                            except Exception as e:
                                print(
                                    f"Error processing page {page_num} of {file}: {str(e)}"
                                )
                                total_errors += 1
                        doc.close()
                    except Exception as e:
                        print(f"Error opening {file}: {str(e)}")
                        total_errors += 1

    print(f"Total PDFs processed: {total_pdfs}")
    print(f"Total PDFs skipped (already processed): {total_skipped}")
    print(f"Total pages processed: {total_pages}")
    print(f"Number of disclaimers found: {total_disclaimers}")
    print(f"Number of errors encountered: {total_errors}")


if __name__ == "__main__":
    # python -m app.services.text_cleanup.training.page_relevance.data_prep
    root_directory = r"G:\My Drive\Startup\NestQ\statements_clustered"
    process_pdfs(root_directory)

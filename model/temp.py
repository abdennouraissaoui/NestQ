import os
import csv
from app.services.text_cleanup.training.exerpt_data_generator import (
    clean_markdown_text,
)
import pyperclip


def read_ocr_text(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except IOError:
        print(f"Error: Unable to read file at {file_path}")
        return None


file_path = "./ocr_texts/bmo.txt"
ocr_text = read_ocr_text(file_path)
cleaned_text = clean_markdown_text(ocr_text)


# Copy cleaned_text to clipboard
pyperclip.copy(cleaned_text)
print("Cleaned text has been copied to clipboard.")

# if ocr_text:
#     # Split the text by two newlines and strip each paragraph
#     paragraphs = [p.strip() for p in ocr_text.split("\n\n") if p.strip()]

#     # Prepare the CSV file path
#     csv_file_path = os.path.join(os.path.dirname(file_path), "bmo_paragraphs.csv")

#     # Write paragraphs to CSV
#     with open(csv_file_path, "w", newline="", encoding="utf-8") as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(["Paragraph"])  # Header
#         for paragraph in paragraphs:
#             writer.writerow([paragraph])

#     print(f"Paragraphs saved to {csv_file_path}")
# else:
#     print("No text to process.")

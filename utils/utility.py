import json
import os
import base64
import pyperclip
import pandas as pd
from datetime import datetime, timezone
import pytz
import re


def dict_to_json_clipboard(dictionary):
    json_str = json.dumps(dictionary, indent=2)  # Format for readability
    pyperclip.copy(json_str)
    print("JSON data copied to clipboard!")


def dataframes_to_string(dataframes, max_rows=7):
    combined_string = ""
    for df in dataframes:
        combined_string += df.head(max_rows).to_string(index=False)
        combined_string += "\n\n"  # Add some spacing between DataFrames
    return combined_string


def load_file_as_base64(file_path) -> str:
    with open(file_path, "rb") as f:
        data = f.read()
    base64_bytes = base64.b64encode(data)
    base64_string = base64_bytes.decode("utf-8")
    return base64_string


def parse_di_table(table):
    data = []
    for row_idx in range(table.row_count):
        row_data = []
        for column_idx in range(table.column_count):
            cell = [
                cell
                for cell in table.cells
                if cell.row_index == row_idx and cell.column_index == column_idx
            ]
            if cell:
                row_data.append(cell[0].content)
            else:
                row_data.append(None)
        data.append(row_data)
    df = pd.DataFrame(data[1:], columns=data[0])
    return df


def epoch_to_utc(epoch_time):
    """Convert Epoch Unix Timestamp to UTC datetime object."""
    return datetime.fromtimestamp(epoch_time, tz=timezone.utc)


def utc_to_epoch(utc_datetime):
    """Convert UTC datetime object to Epoch Unix Timestamp."""
    return int(utc_datetime.timestamp())


def epoch_to_est(epoch_time):
    """Convert Epoch Unix Timestamp to EST datetime object."""
    utc_time = epoch_to_utc(epoch_time)
    est_tz = pytz.timezone("America/New_York")
    return utc_time.astimezone(est_tz)


def est_to_epoch(est_datetime):
    """Convert EST datetime object to Epoch Unix Timestamp."""
    if (
        est_datetime.tzinfo is None
        or est_datetime.tzinfo.utcoffset(est_datetime) is None
    ):
        est_tz = pytz.timezone("America/New_York")
        est_datetime = est_tz.localize(est_datetime)
    return int(est_datetime.timestamp())


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
            if file.lower().endswith(".pdf"):
                # Get the absolute path of the PDF file
                pdf_path = os.path.join(root, file)
                pdf_paths.append(pdf_path)

    return pdf_paths


def clean_markdown_text(ocr_text):
    """
    Cleans markdown text from a PDF and removes duplicate lines.
    """

    # Use regex to remove content between <figure> and </figure> tags, including the tags
    cleaned_text = re.sub(r"<figure>.*?</figure>", "", ocr_text, flags=re.DOTALL)

    # Remove inline HTML tags (except for tables, and page numbers)
    cleaned_text = re.sub(
        r"<(?!table\b|(?:\d+ of \d+)|!--\s*(?:PageNumber|PageFooter)=)[^>]+>",
        "",
        cleaned_text,
    )
    cleaned_text = re.sub(
        r"<!--\s*PageFooter=\"(?!(\d+ of \d+))[^\"]*\"\s*-->", "", cleaned_text
    )

    # Remove links
    cleaned_text = re.sub(r"\[.*?\]\(.*?\)", "", cleaned_text)

    # Remove images
    cleaned_text = re.sub(r"!\[.*?\]\(.*?\)", "", cleaned_text)

    # Remove URLs
    cleaned_text = re.sub(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        "",
        cleaned_text,
    )

    return cleaned_text

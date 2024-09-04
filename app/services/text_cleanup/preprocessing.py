# REFACTOR

from azure.ai.documentintelligence.models import AnalyzeResult
import re


def get_context(layout_analysis: AnalyzeResult) -> str:
    return layout_analysis.content


def is_markdown_structure(line):
    """
    Checks if a line is part of markdown structure (heading, list, table, etc.)
    """
    if not line.strip():
        return False
    return (
        line.startswith("#")
        or line.startswith("- ")
        or line.startswith("* ")
        or re.match(r"\|.*\|", line)
        or line.startswith("<figure>")
        or line.startswith("![")
        or line.startswith("<!--")
        or line.startswith(">")
    )


def clean_markdown_excluding_tables(text):
    """
    Cleans markdown text by removing specific tags and elements while retaining tables.
    Also removes extra spaces and newlines.

    Args:
    - text (str): Input markdown text.

    Returns:
    - str: Cleaned markdown text with tables retained and extra spaces removed.
    """
    # Remove inline HTML tags (except for tables)
    text = re.sub(r"<(?!table\b)[^>]+>", "", text)

    # Remove HTML comments
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)

    # Remove headers
    text = re.sub(r"^# .+", "", text, flags=re.MULTILINE)

    # Remove links
    text = re.sub(r"\[.*?\]\(.*?\)", "", text)

    # Remove images
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)

    # Remove lists
    text = re.sub(r"^- .+", "", text, flags=re.MULTILINE)

    # Remove code blocks
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)

    # Remove inline code
    text = re.sub(r"`[^`]*`", "", text)

    # Remove blockquotes
    text = re.sub(r"^> .+", "", text, flags=re.MULTILINE)

    # Remove footnotes
    text = re.sub(r"\[\d+\]:.*", "", text)
    text = re.sub(r"\[\d+\]", "", text)
    text = re.sub(r"\(\d+\)", "", text)

    # Remove extra spaces and newlines
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"\s{2,}", " ", text)
    text = text.strip()
    return text


def remove_long_continuous_text(text, max_length=1000):
    """
    Removes long continuous paragraphs from text, retaining markdown structures and tables.

    Args:
    - text (str): Input text.
    - max_length (int): Maximum allowed length for a continuous text segment.

    Returns:
    - str: Text with long continuous paragraphs removed.
    """
    lines = text.splitlines()
    cleaned_lines = []
    buffer = []

    for line in lines:
        if is_markdown_structure(line):
            # If we reach a markdown structure, check the buffer
            if len(" ".join(buffer)) > max_length:
                buffer = []  # Clear the buffer if it exceeds max_length
            else:
                cleaned_lines.extend(buffer)  # Keep the buffered text
                buffer = []
            cleaned_lines.append(line)  # Add the current markdown structure
        else:
            buffer.append(line.strip())

    # Check the final buffer
    if len(" ".join(buffer)) <= max_length:
        cleaned_lines.extend(buffer)

    return "\n".join(cleaned_lines).strip()


def clean_text_file(input_path, output_path, max_length=1000):
    """
    Reads text from a file, cleans it by removing long continuous paragraphs,
    and writes the cleaned text to another file.

    Args:
    - input_path (str): Path to the input text file.
    - output_path (str): Path to the output cleaned text file.
    - max_length (int): Maximum allowed length for a continuous text segment.
    """
    # Read the input file
    with open(input_path, "r", encoding="utf-8") as file:
        text = file.read()

    # Clean the text by removing markdown-specific elements (excluding tables)
    text = clean_markdown_excluding_tables(text)

    # Remove long continuous paragraphs
    cleaned_text = remove_long_continuous_text(text, max_length)

    # Write the cleaned text to the output file
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(cleaned_text)


# Example usage
input_file_path = "/home/prixite/Documents/NestQ/app/ocr_texts/wealhsimple.txt"
output_file_path = "wealthsimple_cleaned_text.txt"
clean_text_file(input_file_path, output_file_path, max_length=1000)

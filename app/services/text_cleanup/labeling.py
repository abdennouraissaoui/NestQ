"""
Contains logic for sending each line to an LLM for labeling (whether to keep or delete).
"""

from prompts import LINE_LABELING


def label_line(line):
    response = send_to_openai(prompt)
    return response["label"]  # Assuming OpenAI response includes a 'label' field

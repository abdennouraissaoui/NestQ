import json
import os
import configparser
import base64
import pickle
import pyperclip
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
import pandas as pd
from openai import AzureOpenAI


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


def get_client(client_type: str):
    assert client_type in ["azure-openai", "document-intelligence"]
    config = configparser.ConfigParser()
    # Read absolute path
    config.read(os.path.join(os.path.dirname(__file__), "../nestq.ini"))

    api_key = config.get(client_type, 'API_KEY')
    # an endpoint is a URL at which a web service can be accessed by a client application.
    endpoint = config.get(client_type, 'ENDPOINT')
    if client_type == "azure-openai":
        return AzureOpenAI(api_key=api_key, azure_endpoint=endpoint, api_version="2024-02-01")
    elif client_type == "document-intelligence":
        return DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))


def load_file_as_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    base64_bytes = base64.b64encode(data)
    base64_string = base64_bytes.decode('utf-8')
    return base64_string


def parse_di_table(table):
    data = []
    for row_idx in range(table.row_count):
        row_data = []
        for column_idx in range(table.column_count):
            cell = [cell for cell in table.cells if cell.row_index == row_idx and cell.column_index == column_idx]
            if cell:
                row_data.append(cell[0].content)
            else:
                row_data.append(None)
        data.append(row_data)
    df = pd.DataFrame(data[1:], columns=data[0])
    return df


def save_sample_statements_ocr(sample_layouts: dict):
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, 'sample_statements_ocr.pkl')
    with open(file_path, 'wb') as handle:
        pickle.dump(sample_layouts, handle)


def load_sample_statements_ocr() -> dict:
    # check if file exists. If not, return empty dict
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, 'sample_statements_ocr.pkl')
    if not os.path.isfile(file_path):
        return {}
    with open(file_path, 'rb') as handle:
        sample_layouts = pickle.load(handle)
    return sample_layouts


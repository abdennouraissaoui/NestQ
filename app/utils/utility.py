import json
import os
import base64
import pickle
import pyperclip
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from openai import AzureOpenAI
from app.config import app_config

import pandas as pd

from app.models.schemas import FinancialStatement


def get_ai_client(client_type: str):
    assert client_type in ["azure-openai", "document-intelligence"]
    if client_type == "azure-openai":
        return AzureOpenAI(
            api_key=app_config.AZURE_OPENAI_API_KEY,
            azure_endpoint=app_config.AZURE_OPENAI_ENDPOINT,
            api_version="2024-08-01-preview",
        )
    elif client_type == "document-intelligence":
        return DocumentIntelligenceClient(
            endpoint=app_config.DOCUMENT_INTELLIGENCE_ENDPOINT,
            credential=AzureKeyCredential(app_config.DOCUMENT_INTELLIGENCE_API_KEY),
        )


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


def load_file_as_base64(file_path):
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


def save_sample_statements_ocr(sample_layouts: dict):
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "sample_statements_ocr.pkl")
    with open(file_path, "wb") as handle:
        pickle.dump(sample_layouts, handle)


def load_sample_statements_ocr() -> dict:
    # check if file exists. If not, return empty dict
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "sample_statements_ocr.pkl")
    if not os.path.isfile(file_path):
        return {}
    with open(file_path, "rb") as handle:
        sample_layouts = pickle.load(handle)
    return sample_layouts


def output_to_excel(statement_data: FinancialStatement):
    # Create a Pandas Excel writer using XlsxWriter as the engine
    # Random file name
    file_name = "output.xlsx"
    with pd.ExcelWriter(file_name, engine="xlsxwriter") as writer:
        # Client Information
        client_info = {
            "First Name": statement_data.client.first_name,
            "Last Name": statement_data.client.last_name,
            "Unit Number": statement_data.client.client_unit_number,
            "Street Number": statement_data.client.client_street_number,
            "Street Name": statement_data.client.client_street_name,
            "City": statement_data.client.client_city,
            "Province": statement_data.client.client_province,
            "Postal Code": statement_data.client.client_postal_code,
            "Country": statement_data.client.client_country,
        }
        client_df = pd.DataFrame(list(client_info.items()), columns=["Field", "Value"])
        client_df.to_excel(writer, sheet_name="Client Information", index=False)

        # Account Information
        for account in statement_data.accounts:
            account_info = {
                "Account Type": account.account_type.value,
                "Account ID": account.account_id,
                "Account Value": f"${account.account_value:,.2f}",
                "Cash value": f"${account.cash_balance:,.2f}",
                "Management Fee Amount": f"${account.management_fee_amount:,.2f}",
                "Estimated MER": f"{account.management_fee_amount / account.account_value * 100 * 12:.2f}%",
                "Statement Start Date": account.statement_start_date,
                "Statement End Date": account.statement_end_date,
            }
            account_df = pd.DataFrame(
                list(account_info.items()), columns=["Field", "Value"]
            )
            account_df.to_excel(
                writer, sheet_name=f"{account.account_id}_info", index=False
            )

            # Account Holdings
            holdings = pd.DataFrame(
                [holding.model_dump() for holding in account.holdings]
            )
            # combined_df = pd.concat([account_df, pd.DataFrame([[]]), holdings], ignore_index=True)

            holdings.to_excel(
                writer, sheet_name=f"{account.account_id}_holdings", index=False
            )

    print(f"Data exported to {file_name}")

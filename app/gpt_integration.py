from app.prompts import FinancialStatement, INVESTMENT_STATEMENT_DATA_EXTRACTION
import instructor
from app.utility import get_client, load_sample_statements_ocr
import pandas as pd


def output_to_excel(statement_data: FinancialStatement):
    # Create a Pandas Excel writer using XlsxWriter as the engine
    # Random file name
    file_name = 'output.xlsx'
    with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
        # Client Information
        client_info = {
            'First Name': statement_data.client.first_name,
            'Last Name': statement_data.client.last_name,
            'Unit Number': statement_data.client.client_unit_number,
            'Street Number': statement_data.client.client_street_number,
            'Street Name': statement_data.client.client_street_name,
            'City': statement_data.client.client_city,
            'Province': statement_data.client.client_province,
            'Postal Code': statement_data.client.client_postal_code,
            'Country': statement_data.client.client_country
        }
        client_df = pd.DataFrame(list(client_info.items()), columns=['Field', 'Value'])
        client_df.to_excel(writer, sheet_name='Client Information', index=False)

        # Account Information
        for account in statement_data.accounts:
            account_info = {
                'Account Type': account.account_type.value,
                'Account ID': account.account_id,
                'Account Value': f"${account.account_value:,.2f}",
                'Cash value': f"${account.cash_balance:,.2f}",
                'Management Fee Amount': f"${account.management_fee_amount:,.2f}",
                'Estimated MER': f"{account.management_fee_amount / account.account_value * 100 * 12:.2f}%",
                'Statement Start Date': account.statement_start_date,
                'Statement End Date': account.statement_end_date,
            }
            account_df = pd.DataFrame(list(account_info.items()), columns=['Field', 'Value'])
            account_df.to_excel(writer, sheet_name=f'{account.account_id}_info', index=False)

            # Account Holdings
            holdings = pd.DataFrame([holding.model_dump() for holding in account.holdings])
            # combined_df = pd.concat([account_df, pd.DataFrame([[]]), holdings], ignore_index=True)

            holdings.to_excel(writer, sheet_name=f'{account.account_id}_holdings', index=False)

    print(f"Data exported to {file_name}")


def get_structured_data(context) -> FinancialStatement:
    client = instructor.from_openai(get_client("azure-openai"))
    response = client.chat.completions.create(
        model="gpt-4",
        response_model=FinancialStatement,
        max_retries=4,
        temperature=0.2,
        messages=[
            {"role": "system", "content": INVESTMENT_STATEMENT_DATA_EXTRACTION['system']},
            {"role": "user",
             "content": INVESTMENT_STATEMENT_DATA_EXTRACTION['user'].format(statement_text=context)}
        ])
    # TODO: Add error handling, maybe found in https://python.useinstructor.com/
    return response


if __name__ == '__main__':
    import time
    sample_statements = load_sample_statements_ocr()
    sample_statement = sample_statements['nbin.pdf']
    parse_start_time = time.time()
    structured_data = get_structured_data(sample_statement.content)
    output_to_excel(structured_data)
    print(f"Selected item parsed in {time.time() - parse_start_time:.2f} seconds")
    print(structured_data)

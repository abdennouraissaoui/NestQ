import time
import streamlit as st
import pandas as pd

from app.gpt_integration import get_structured_data
from app.prompts import FinancialStatement
from app.utility import load_sample_statements_ocr


start_time = time.time()
sample_statements: dict = load_sample_statements_ocr()
st.write(f"Sample statements loaded in {time.time() - start_time:.2f} seconds")

# Streamlit app
def main():
    st.title("Investment Statement Viewer")
    # Description
    st.write("""
    This app allows you to select a sample statement from the list below and retrieves holdings information.
    """)

    # Sample list of items
    items = list(sample_statements.keys())
    print(items)

    # User selects an item from the list
    selected_item = st.selectbox("Select a sample statement", items)

    if selected_item:
        # Parse the selected item
        parse_start_time = time.time()
        statement_data: FinancialStatement = get_structured_data(sample_statements[selected_item].content)
        st.write(f"Selected item parsed in {time.time() - parse_start_time:.2f} seconds")

        # Display client information
        st.header("Client Information")
        st.write(f"**First Name:** {statement_data.client.first_name}")
        st.write(f"**Last Name:** {statement_data.client.last_name}")
        st.write(f"**Address:** {statement_data.client.client_unit_number} {statement_data.client.client_street_number} {statement_data.client.client_street_name}, {statement_data.client.client_city}, {statement_data.client.client_province} {statement_data.client.client_postal_code}, {statement_data.client.client_country}")

        for account in statement_data.accounts:
            st.header(f"Account {account.account_id} Information")
            st.write(f"**Account Type:** {account.account_type.value}")
            st.write(f"**Account ID:** {account.account_id}")
            st.write(f"**Statement Start Date:** {account.statement_start_date}")
            st.write(f"**Statement End Date:** {account.statement_end_date}")
            st.write(f"**Account Value:** ${account.account_value:,.2f}")
            st.write(f"**Management Fee Amount:** ${account.management_fee_amount:,.2f}")
            holdings = pd.DataFrame([holding.model_dump() for holding in account.holdings])
            st.header(f"Account {account.account_id} Holdings")
            st.table(holdings)

if __name__ == "__main__":
    main()
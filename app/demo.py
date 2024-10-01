import time
import streamlit as st
import pandas as pd
from app.services.statement_extractor import FinancialStatementProcessor
import base64  # Add this import


start_time = time.time()
st.write(f"Sample statements loaded in {time.time() - start_time:.2f} seconds")


# Streamlit app
def main():
    st.title("Investment Statement Viewer")
    st.write("""
    This app allows you to upload an investment statement PDF and view the extracted information.
    """)

    # File uploader
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        # Save the uploaded file temporarily

        # Convert the uploaded file to base64
        file_base64 = base64.b64encode(uploaded_file.getvalue()).decode(
            "utf-8"
        )  # {{ edit_1 }}

        # Extract data from the uploaded statement
        parse_start_time = time.time()
        extractor = FinancialStatementProcessor()
        scan_update, statement_data = extractor.process_scan(
            file_base64=file_base64  # {{ edit_2 }}
        )
        st.write(
            f"Statement parsed in {time.time() - parse_start_time:.2f} seconds"
        )

        # Display account information
        for account in statement_data.accounts:
            st.header(f"Account {account.account_id or 'N/A'} Information")
            st.write(
                f"**Account Type:** {account.account_type.value if account.account_type else 'N/A'}"
            )
            st.write(f"**Account ID:** {account.account_id or 'N/A'}")
            st.write(
                f"**Account Value:** ${account.account_value:,.2f}"
                if account.account_value is not None
                else "**Account Value:** N/A"
            )
            st.write(
                f"**Cash value:** ${account.cash_balance:,.2f}"
                if account.cash_balance is not None
                else "**Cash value:** N/A"
            )
            st.write(
                f"**Management Fee Amount:** ${account.management_fee_amount:,.2f}"
                if account.management_fee_amount is not None
                else "**Management Fee Amount:** N/A"
            )
            holdings = pd.DataFrame(
                [holding.model_dump() for holding in account.holdings]
            )
            st.header(f"Account {account.account_id} Holdings")
            st.dataframe(holdings, use_container_width=True)


if __name__ == "__main__":
    main()

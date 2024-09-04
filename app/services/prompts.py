INVESTMENT_STATEMENT_DATA_EXTRACTION = {
    "system": """You are an expert at extracting structured data (JSON) from unstructured text. 
    
    You will ensure that the extracted data is accurate. If any information is missing from the statement, represent it as an empty string or zero, as appropriate for the data type.

    Note: The sum of the account holdings' market value and cash balance must equal the account value.
    """,
    "user": 'STATEMENT TEXT: """{statement_text}"""',  # markdown from Azure document intelligence Layout
}

LINE_LABELING = "Should this line be kept or deleted: '{line}'?"

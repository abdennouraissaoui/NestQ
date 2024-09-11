INVESTMENT_STATEMENT_DATA_EXTRACTION = {
    "system": """You are an expert at extracting structured data (JSON) from unstructured text. 
    
    You will ensure that the extracted data is accurate. If any information is missing from the statement, represent it as an empty string or zero, as appropriate for the data type.

    Note: The sum of the account holdings' total market value must equal the account value. Cash is also considered a holding.
    """,
    "user": 'STATEMENT TEXT: """{statement_text}"""',  # markdown from Azure document intelligence Layout
}

DISCLAIMER_PAGE_CLASSIFICATION_PROMPT = {
    "system": """You are an expert at identifying the disclaimer page in an investment statement.
    
    You will ensure that the classification is accurate. Note that headers and footers may contain account numbers and/or names, but these should not affect the classification of the page as a disclaimer or non-disclaimer.

    A disclaimer page typically contains legal text, general terms and conditions, or standard disclosures. Pages with user-specific information (other than account numbers and names) such as account summaries, portfolio details, or personalized financial data should not be classified as disclaimers.

    Provide a JSON response with the following keys:
    - "exclude": 1 if the text is primarily disclaimer text (ignoring headers and footers), 0 if the text contains significant user-specific information or financial data""",
    "user": """
    PAGE TEXT:
    "{text}"
    """,
}

STANDARD_TEXT_CLASSIFICATION_PROMPT = {
    "system": """
    Classify investment statement excerpts as 'generic' (boilerplate/disclaimer) or 'non-generic' (user-specific/structural).

    Guidelines:
    1. Keep: Names, addresses, tables, account numbers, statement date, and document structure elements (headers, subheaders, formatting)
    2. Exclude: Common legal disclaimers, general product descriptions, standardized text, etc.
    
    Note: Classify mixed content as non-generic if contains any specific information.

    Output JSON:
    - "exclude": 0 if not generic, 1 if boilerplate/legal/disclaimer.""",
    "user": """
    Excerpt:
    "{text}"
    """,
}

INVESTMENT_STATEMENT_DATA_EXTRACTION = {
    "system": """You are an expert at extracting structured data (JSON) from unstructured text. 
    
    You will ensure that the extracted data is accurate. If any information is missing from the statement, represent it as an empty string or zero, as appropriate for the data type.

    Note: The sum of the account holdings' total market value must equal the account value.
    """,
    "user": 'STATEMENT TEXT: """{statement_text}"""',  # markdown from Azure document intelligence Layout
}

DISCLAIMER_PAGE_CLASSIFICATION_PROMPT = {
    "system": """You are an expert at identifying the disclaimer page in an investment statement.
    
    You will ensure that the classification is accurate. Provide a JSON response with the following keys:
    - "is_disclaimer": 1 if the text is disclaimer text only, 0 if the text is user-specific""",
    "user": """
    PAGE TEXT TO CLASSIFY:
    "{text}"
    """,
}

STANDARD_TEXT_CLASSIFICATION_PROMPT = {
    "system": """You are an expert at identifying whether a paragraph from an investment statement contains generic information or user-specific information.
    
    You will ensure that the classification is accurate. Provide a JSON response with the following keys:
    - "is_generic": 1 if the text contains only generic information, 0 if it contains user-specific information""",
    "user": """
    TEXT CONTENT TO CLASSIFY:
    "{text}"
    """,
}

from app.models.schemas import FinancialStatement, INVESTMENT_STATEMENT_DATA_EXTRACTION
from app.utils.misc import output_to_excel


def get_structured_data_instructor(context) -> FinancialStatement:
    import instructor

    client = instructor.from_openai(get_client("azure-openai"))
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_model=FinancialStatement,
        max_retries=2,
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": INVESTMENT_STATEMENT_DATA_EXTRACTION["system"],
            },
            {
                "role": "user",
                "content": INVESTMENT_STATEMENT_DATA_EXTRACTION["user"].format(
                    statement_text=context
                ),
            },
        ],
    )
    # TODO: Add error handling, maybe found in https://python.useinstructor.com/
    return response


def get_structured_data(context: str):
    client = get_client("azure-openai")
    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": INVESTMENT_STATEMENT_DATA_EXTRACTION["system"],
            },
            {
                "role": "user",
                "content": INVESTMENT_STATEMENT_DATA_EXTRACTION["user"].format(
                    statement_text=context
                ),
            },
        ],
        response_format=FinancialStatement,
    )
    print(completion.model_dump_json(indent=2))
    return completion.choices[0].message.parsed


if __name__ == "__main__":
    import time
    # from app.utils.utility import get_client, load_sample_statements_ocr

    # sample_statements = load_sample_statements_ocr()
    # sample_statement = sample_statements["bmo.pdf"]
    sample_statement = open("../cleaned_texts/nbin_cleaned_text.txt", "r").read()
    parse_start_time = time.time()
    structured_data = get_structured_data(sample_statement)
    output_to_excel(structured_data)
    print(f"Selected item parsed in {time.time() - parse_start_time:.2f} seconds")
    print(structured_data)

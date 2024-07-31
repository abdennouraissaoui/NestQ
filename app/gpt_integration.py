from app.prompts import FinancialStatement, INVESTMENT_STATEMENT_DATA_EXTRACTION
import instructor
from app.utility import get_client, load_sample_statements_ocr


def get_structured_data(context):
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
    sample_statements = load_sample_statements_ocr()
    sample_statement = sample_statements[list(sample_statements.keys())[0]]
    structured_data = get_structured_data(sample_statement.content)
    print(structured_data)
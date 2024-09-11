"""
Orchestrates the extraction of holdings from a financial statement.
"""

from app.services.text_cleanup import get_llm_ready_text
from app.services.prompts import INVESTMENT_STATEMENT_DATA_EXTRACTION
from app.models.schemas import FinancialStatement
from app.services.llm_factory import LlmFactory


class StatementExtractor:
    def __init__(self, input_file_path: str, llm_provider: str = "azure-openai"):
        self.input_file_path = input_file_path
        self.llm_factory = LlmFactory(llm_provider)

    def extract_financial_statement(self) -> FinancialStatement:
        try:
            # Step 1: Get LLM-ready text
            llm_ready_text = get_llm_ready_text(self.input_file_path)

            # Step 2: Prepare the prompt
            messages = [
                {
                    "role": "system",
                    "content": INVESTMENT_STATEMENT_DATA_EXTRACTION["system"],
                },
                {
                    "role": "user",
                    "content": INVESTMENT_STATEMENT_DATA_EXTRACTION["user"].format(
                        statement_text=llm_ready_text
                    ),
                },
            ]

            # Step 3: Call LLM and parse response
            completion = self.llm_factory.create_completion(
                model="gpt-4o",
                response_format=FinancialStatement,
                messages=messages,
            )

            # Step 4: Return the parsed FinancialStatement object
            return completion.choices[0].message.parsed

        except FileNotFoundError:
            raise FileNotFoundError(f"Input file not found: {self.input_file_path}")
        except Exception as e:
            raise RuntimeError(
                f"An error occurred during statement extraction: {str(e)}"
            )


# Example usage
if __name__ == "__main__":
    import time

    start_time = time.time()
    extractor = StatementExtractor("./model/data/sample_statements/CI.pdf")
    financial_statement = extractor.extract_financial_statement()
    end_time = time.time()

    print(f"Execution time: {end_time - start_time:.2f} seconds")
    print(financial_statement)

from openai import AzureOpenAI
from pydantic import BaseModel
from typing import List, Dict, Type, Any
from app.config import app_config
from openai import OpenAI


class LlmFactory:
    def __init__(self, provider: str):
        self.provider = provider
        self.client = self._initialize_client()

    def _initialize_client(self) -> Any:
        assert self.provider in ["azure-openai", "local-lm-studio"]
        if self.provider == "azure-openai":
            return AzureOpenAI(
                api_key=app_config.AZURE_OPENAI_API_KEY,
                azure_endpoint=app_config.AZURE_OPENAI_ENDPOINT,
                api_version="2024-08-01-preview",
            )
        elif self.provider == "local-lm-studio":
            return OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="not-needed")

    def create_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        response_format: Type[BaseModel] | None = None,
        **kwargs,
    ) -> Any:
        completion_params = {
            "model": model,
            "temperature": kwargs.get("temperature", 0.2),
            "messages": messages,
        }
        if response_format:
            completion_params["response_format"] = response_format
            return self.client.beta.chat.completions.parse(**completion_params)
        return self.client.chat.completions.create(**completion_params)


if __name__ == "__main__":
    from app.models.schemas import FinancialStatement
    from app.services.prompts import INVESTMENT_STATEMENT_DATA_EXTRACTION
    from pydantic import Field
    import time
    # from app.utils.utility import load_sample_statements_ocr

    llm = LlmFactory("local-lm-studio")

    class CompletionModel(BaseModel):
        response: str = Field(description="Your response to the user.")
        reasoning: str = Field(description="Explain your reasoning for the response.")

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "If it takes 2 hours to dry 1 shirt out in the sun, how long will it take to dry 5 shirts?",
        },
    ]

    completion = llm.create_completion(
        response_format=CompletionModel,
        messages=messages,
        model="meta-llama-3.1-8b-instruct-q4_k_m",
    )

    parsed_response = completion.choices[0].message.parsed
    print(f"Parsed response: {parsed_response}")

    completion = llm.create_completion(messages=messages, model="gpt-4o-mini")
    print(completion.choices[0].message)

    # sample_statements = load_sample_statements_ocr()
    # sample_statement = sample_statements["bmo.pdf"]
    sample_statement = open(
        "./cleaned_texts/nbin_cleaned_text.txt", "r", encoding="utf-8"
    ).read()
    parse_start_time = time.time()
    completion = llm.create_completion(
        model="gpt-4o",
        response_format=FinancialStatement,
        messages=[
            {
                "role": "system",
                "content": INVESTMENT_STATEMENT_DATA_EXTRACTION["system"],
            },
            {
                "role": "user",
                "content": INVESTMENT_STATEMENT_DATA_EXTRACTION["user"].format(
                    statement_text=sample_statement
                ),
            },
        ],
    )
    structured_data = completion.choices[0].message.parsed
    # output_to_excel(structured_data)
    print(f"Selected item parsed in {time.time() - parse_start_time:.2f} seconds")
    print(structured_data)

from openai import AsyncAzureOpenAI
from pydantic import BaseModel
from typing import List, Dict, Type, Any
from app.config import app_config
from openai import AsyncOpenAI


class LlmFactory:
    def __init__(self, provider: str):
        self.provider = provider
        self.client = self._initialize_client()

    def _initialize_client(self) -> Any:
        assert self.provider in ["azure-openai", "local-lm-studio"]
        if self.provider == "azure-openai":
            return AsyncAzureOpenAI(
                api_key=app_config.AZURE_OPENAI_API_KEY,
                azure_endpoint=app_config.AZURE_OPENAI_ENDPOINT,
                api_version="2024-08-01-preview",
            )
        elif self.provider == "local-lm-studio":
            return AsyncOpenAI(
                base_url="http://127.0.0.1:1234/v1", api_key="not-needed"
            )

    async def create_completion(
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
            "logprobs": True,
        }
        if response_format:
            completion_params["response_format"] = response_format
            return await self.client.beta.chat.completions.parse(
                **completion_params
            )
        return await self.client.chat.completions.create(**completion_params)


if __name__ == "__main__":
    from pydantic import Field
    import asyncio

    llm = LlmFactory("azure-openai")
    # llm = LlmFactory("local-lm-studio")

    class CompletionModel(BaseModel):
        response: str = Field(description="Your response to the user.")
        reasoning: str = Field(
            description="Explain your reasoning for the response."
        )

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        # {
        #     "role": "user",
        #     "content": "If it takes 2 hours to dry 1 shirt out in the sun, how long will it take to dry 5 shirts?",
        # },
    ]
    messages.append({
        "role": "user",
        "content": "What is the MER of PIMCO MONTHLY INCOME FUND SR A?",
    })

    completion = asyncio.run(
        llm.create_completion(
            # response_format=CompletionModel,
            messages=messages,
            model="gpt-4o",
        )
    )
    print(completion.choices[0].message)

    # parsed_response = completion.choices[0].message.parsed
    # print(f"Parsed response: {parsed_response}")

    # completion = llm.create_completion(messages=messages, model="gpt-4o-mini")
    # print(completion.choices[0].message)

from openai import AsyncOpenAI, OpenAIError
from openai.types.responses import Response

from portfolio_analyzer.exceptions.llm_service import LLMServiceError


class LLMService:
    def __init__(self, client: AsyncOpenAI) -> None:
        self.client = client

    async def analyse(self, prompt: str) -> str:
        try:
            response: Response = await self.client.responses.create(
                model="gpt-5.6-luna",
                input=prompt,
            )
            return response.output_text

        except OpenAIError as exc:
            raise LLMServiceError(
                "LLM service error."
            ) from exc

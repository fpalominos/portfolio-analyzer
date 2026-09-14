from openai import AsyncOpenAI, OpenAIError
from openai.types.responses import ParsedResponse

from portfolio_analyzer.exceptions.llm_service import LLMServiceError
from portfolio_analyzer.models.portfolio_analysis import PortfolioAnalysis


class LLMService:
    def __init__(self, client: AsyncOpenAI) -> None:
        self.client = client

    async def analyse(self, prompt: str) -> PortfolioAnalysis:
        try:
            response: ParsedResponse[PortfolioAnalysis] = await self.client.responses.parse(
                text_format=PortfolioAnalysis,
                model="gpt-5.6-luna",
                input=prompt,
            )

            parsed: PortfolioAnalysis | None = response.output_parsed

            if parsed is None:
                raise LLMServiceError(
                    "LLM returned no structured output."
                )

            return parsed

        except OpenAIError as exc:
            raise LLMServiceError(
                "LLM service error."
            ) from exc

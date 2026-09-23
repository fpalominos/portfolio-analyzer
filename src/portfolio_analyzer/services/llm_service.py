import json

from openai import AsyncOpenAI, OpenAIError
from openai.types.responses import ParsedResponse

from portfolio_analyzer.exceptions.llm_service import LLMServiceError
from portfolio_analyzer.models.portfolio_analysis import PortfolioAnalysis
from portfolio_analyzer.services.price_service import PriceService
from portfolio_analyzer.tools.definitions import get_stock_price_tool
from portfolio_analyzer.tools.stock_tools import get_stock_price


class LLMService:
    def __init__(self, client: AsyncOpenAI, price_service: PriceService) -> None:
        self.client = client
        self.price_service = price_service

    async def analyse(self, prompt: str) -> PortfolioAnalysis:
        try:
            response: ParsedResponse[PortfolioAnalysis] = await self.client.responses.parse(
                text_format=PortfolioAnalysis,
                model="gpt-5.6-luna",
                input=prompt,
                tools=[get_stock_price_tool()]
            )

            final_response = response

            tool_outputs = []

            for item in response.output:
                if getattr(item, "type", None) == "function_call":
                    arguments = json.loads(str(item.arguments))
                    symbol = arguments["symbol"]

                    tool_result = await get_stock_price(
                        symbol,
                        self.price_service,
                    )

                    tool_outputs.append(
                        {
                            "type": "function_call_output",
                            "call_id": item.call_id,
                            "output": str(tool_result),
                        }
                    )

            if tool_outputs:
                final_response = await self.client.responses.parse(
                    text_format=PortfolioAnalysis,
                    model="gpt-5.6-luna",
                    input=tool_outputs,
                    tools=[get_stock_price_tool()],
                    # Link this request to the previous response so OpenAI can associate the tool result
                    # with its function call and continue the response chain, even if other requests
                    # are handled by the service in between.
                    previous_response_id=response.id,
                )

            parsed: PortfolioAnalysis | None = final_response.output_parsed

            if parsed is None:
                raise LLMServiceError(
                    "LLM returned no structured output."
                )

            return parsed

        except OpenAIError as exc:
            raise LLMServiceError(
                "LLM service error."
            ) from exc

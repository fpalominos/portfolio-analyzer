import asyncio
import json

from openai import AsyncOpenAI, OpenAIError
from openai.types.responses import ParsedResponse

from portfolio_analyzer.analytics.portfolio_analytics import PortfolioAnalytics
from portfolio_analyzer.exceptions.llm_service import LLMServiceError
from portfolio_analyzer.models.portfolio_analysis import PortfolioAnalysis
from portfolio_analyzer.repositories.portfolio_repository import PortfolioRepository
from portfolio_analyzer.services.portfolio_valuator import PortfolioValuator
from portfolio_analyzer.services.price_service import PriceService
from portfolio_analyzer.tools.definitions import get_stock_price_tool, get_allocation_tool
from portfolio_analyzer.tools.registry import build_tool_registry


class LLMService:
    def __init__(self, client: AsyncOpenAI, price_service: PriceService, portfolio_repository: PortfolioRepository,
                 portfolio_valuator: PortfolioValuator, portfolio_analytics: PortfolioAnalytics) -> None:
        self.client = client
        self.price_service = price_service
        self.portfolio_repository = portfolio_repository
        self.portfolio_valuator = portfolio_valuator
        self.portfolio_analytics = portfolio_analytics
        self.tool_registry = build_tool_registry(price_service, portfolio_repository, portfolio_valuator,
                                                 portfolio_analytics)

    async def analyse(self, prompt: str) -> PortfolioAnalysis:
        try:
            response: ParsedResponse[PortfolioAnalysis] = await self.client.responses.parse(
                text_format=PortfolioAnalysis,
                model="gpt-5.6-luna",
                input=prompt,
                tools=[get_stock_price_tool(), get_allocation_tool()]
            )

            while True:
                call_ids, tool_result_tasks = self._extract_tool_calls(response)

                if not tool_result_tasks:
                    break

                tool_outputs = await self._build_tool_outputs(
                    call_ids,
                    tool_result_tasks,
                )

                response = await self.client.responses.parse(
                    text_format=PortfolioAnalysis,
                    model="gpt-5.6-luna",
                    input=tool_outputs,
                    tools=[get_stock_price_tool(), get_allocation_tool()],
                    # Link this request to the previous response so OpenAI can associate the tool result
                    # with its function call and continue the response chain, even if other requests
                    # are handled by the service in between.
                    previous_response_id=response.id,
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

    async def _build_tool_outputs(self, call_ids: list[str], tool_result_tasks: list) -> list[dict[str, str]]:
        tool_results = await asyncio.gather(*tool_result_tasks)
        tool_outputs = [
            {
                "type": "function_call_output",
                "call_id": call_id,
                "output": self._serialize_tool_result(tool_result),
            }
            for tool_result, call_id in zip(tool_results, call_ids)
        ]
        return tool_outputs

    def _serialize_tool_result(self, result: object):
        if isinstance(result, tuple):
            return json.dumps([
                r.model_dump(mode="json")
                for r in result
            ])
        else:
            return json.dumps(result)

    def _extract_tool_calls(self, response: ParsedResponse[PortfolioAnalysis]) -> tuple[
        list[str], list]:
        tool_result_tasks = []
        call_ids = []

        for item in response.output:
            if getattr(item, "type", None) == "function_call":
                function_call_name = str(getattr(item, "name", None))
                executor_details = self.tool_registry[function_call_name]
                dependencies = executor_details['dependencies']
                arguments = json.loads(str(item.arguments))
                llm_argument_names = executor_details['llm_arguments']

                llm_argument_values = []
                for argument_name in llm_argument_names:
                    argument_value = arguments[argument_name]
                    llm_argument_values.append(argument_value)

                executor_args = llm_argument_values + dependencies
                call_ids.append(item.call_id)
                task = executor_details["executor"](*executor_args)

                tool_result_tasks.append(task)

        return call_ids, tool_result_tasks

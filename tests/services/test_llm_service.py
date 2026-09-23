from unittest.mock import AsyncMock, Mock, patch

import pytest
from openai import OpenAIError

from portfolio_analyzer.exceptions.llm_service import LLMServiceError
from portfolio_analyzer.models.portfolio_analysis import PortfolioAnalysis
from portfolio_analyzer.services.llm_service import LLMService
from portfolio_analyzer.services.price_service import PriceService
from portfolio_analyzer.tools.definitions import get_stock_price_tool
from portfolio_analyzer.tools.stock_tools import get_stock_price

# parse() is the async operation we await, so it is represented by an AsyncMock.
# The Response returned by parse() is a normal object, so a regular Mock is enough.
# The fact that client is an AsyncMock means its methods are automatically mocked as asynchronous operations. So client.responses.parse acts as an AsyncMock child
"""
client = AsyncMock()
       ↓
responses.parse() = AsyncMock
       ↓ await
fake_response = Mock
       ↓
output_parsed
"""


@pytest.mark.asyncio
async def test_analyse_returns_portfolio_analysis(
        portfolio_analysis
):
    client = AsyncMock()

    fake_response = Mock()
    fake_response.output = []
    fake_response.output_parsed = portfolio_analysis

    client.responses.parse.return_value = fake_response

    price_service = Mock(spec=PriceService)
    service = LLMService(client, price_service)

    result = await service.analyse("Analyse my portfolio")

    assert result == portfolio_analysis

    client.responses.parse.assert_awaited_once_with(
        text_format=PortfolioAnalysis,
        model="gpt-5.6-luna",
        input="Analyse my portfolio",
        tools=[get_stock_price_tool()],
    )


@pytest.mark.asyncio
@patch("portfolio_analyzer.services.llm_service.get_stock_price")
async def test_analyse_handles_stock_price_tool_call(mock_get_stock_price):
    client = AsyncMock()

    tool_call = Mock()
    tool_call.type = "function_call"
    tool_call.name = "get_stock_price"
    tool_call.arguments = '{"symbol": "NVDA"}'
    tool_call.call_id = "call_123"

    fake_response = Mock()
    fake_response.output = [tool_call]
    fake_response.id = "response_123"

    assert fake_response.output[0].type == "function_call"
    assert fake_response.output[0].name == "get_stock_price"
    assert fake_response.output[0].arguments == '{"symbol": "NVDA"}'

    final_response = Mock()
    final_response.output_parsed = PortfolioAnalysis(
        summary="test summary",
        diversification="test diversification",
        risks=["test risk"],
        recommendations=["test recommendation"],
    )

    client.responses.parse.side_effect = [
        fake_response,
        final_response,
    ]

    price_service = Mock(spec=PriceService)

    mock_get_stock_price.return_value = 250.00

    service = LLMService(client, price_service)

    result = await service.analyse("What is the current price of Nvidia?")

    mock_get_stock_price.assert_awaited_once_with("NVDA", price_service)

    assert client.responses.parse.await_count == 2

    second_call = client.responses.parse.await_args_list[1]

    assert second_call.kwargs["input"] == [
        {
            "type": "function_call_output",
            "call_id": "call_123",
            "output": "250.0",
        }
    ]

    assert second_call.kwargs["previous_response_id"] == "response_123"

    assert result == PortfolioAnalysis(
        summary="test summary",
        diversification="test diversification",
        risks=["test risk"],
        recommendations=["test recommendation"],
    )


@pytest.mark.asyncio
async def test_analyse_raises_llm_service_error_for_no_structured_output():
    client = AsyncMock()

    fake_response = Mock()
    fake_response.output = []
    fake_response.output_parsed = None

    client.responses.parse.return_value = fake_response

    price_service = Mock(spec=PriceService)
    service = LLMService(client, price_service)

    with pytest.raises(LLMServiceError) as excinfo:
        await service.analyse("Analyse my portfolio")

    assert str(excinfo.value) == "LLM returned no structured output."


@pytest.mark.asyncio
async def test_analyse_raises_llm_service_error_for_openai_error():
    client = AsyncMock()

    client.responses.parse.side_effect = OpenAIError("Something went wrong")

    price_service = Mock(spec=PriceService)
    service = LLMService(client, price_service)
    with pytest.raises(LLMServiceError) as excinfo:
        await service.analyse("Analyse my portfolio")

    assert str(excinfo.value) == "LLM service error."

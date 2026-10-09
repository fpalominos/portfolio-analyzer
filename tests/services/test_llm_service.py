import json
from unittest.mock import AsyncMock, Mock, patch, call
from unittest.mock import create_autospec

import pytest
from openai import OpenAIError

from portfolio_analyzer.analytics.portfolio_analytics import PortfolioAnalytics
from portfolio_analyzer.exceptions.llm_service import LLMServiceError
from portfolio_analyzer.models.portfolio_analysis import PortfolioAnalysis
from portfolio_analyzer.repositories.portfolio_repository import PortfolioRepository
from portfolio_analyzer.services.llm_service import LLMService
from portfolio_analyzer.services.portfolio_valuator import PortfolioValuator
from portfolio_analyzer.services.price_service import PriceService
from portfolio_analyzer.tools.definitions import get_stock_price_tool, get_allocation_tool
from portfolio_analyzer.tools.stock_tools import AllocationResult

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
    portfolio_valuator = Mock(spec=PortfolioValuator)
    portfolio_repository = create_autospec(PortfolioRepository)
    portfolio_analytics = Mock(spec=PortfolioAnalytics)

    service = LLMService(client, price_service, portfolio_repository, portfolio_valuator, portfolio_analytics)

    result = await service.analyse("Analyse my portfolio")

    assert result == portfolio_analysis

    client.responses.parse.assert_awaited_once_with(
        text_format=PortfolioAnalysis,
        model="gpt-5.6-luna",
        input="Analyse my portfolio",
        tools=[get_stock_price_tool(), get_allocation_tool()],
    )


@pytest.mark.asyncio
@patch("portfolio_analyzer.tools.registry.get_stock_price")
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

    final_response = Mock()
    final_response.output = []
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

    portfolio_valuator = Mock(spec=PortfolioValuator)
    portfolio_repository = create_autospec(PortfolioRepository)
    portfolio_analytics = Mock(spec=PortfolioAnalytics)

    service = LLMService(client, price_service, portfolio_repository, portfolio_valuator, portfolio_analytics)

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
@patch("portfolio_analyzer.tools.registry.get_stock_price")
async def test_analyse_handles_multiple_stock_price_tool_calls(mock_get_stock_price):
    client = AsyncMock()

    tool_call_1 = Mock()
    tool_call_1.type = "function_call"
    tool_call_1.name = "get_stock_price"
    tool_call_1.arguments = '{"symbol": "NVDA"}'
    tool_call_1.call_id = "call_1"

    tool_call_2 = Mock()
    tool_call_2.type = "function_call"
    tool_call_2.name = "get_stock_price"
    tool_call_2.arguments = '{"symbol": "AAPL"}'
    tool_call_2.call_id = "call_2"

    tool_call_3 = Mock()
    tool_call_3.type = "function_call"
    tool_call_3.name = "get_stock_price"
    tool_call_3.arguments = '{"symbol": "MSFT"}'
    tool_call_3.call_id = "call_3"

    fake_response = Mock()
    fake_response.output = [tool_call_1, tool_call_2, tool_call_3]
    fake_response.id = "response_123"

    final_response = Mock()
    final_response.output = []
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

    async def get_stock_price_side_effect(symbol, _price_service):
        prices = {
            "NVDA": 250.00,
            "AAPL": 260.00,
            "MSFT": 270.00,
        }
        return prices[symbol]

    mock_get_stock_price.side_effect = get_stock_price_side_effect

    portfolio_valuator = Mock(spec=PortfolioValuator)
    portfolio_repository = create_autospec(PortfolioRepository)
    portfolio_analytics = Mock(spec=PortfolioAnalytics)

    service = LLMService(client, price_service, portfolio_repository, portfolio_valuator, portfolio_analytics)

    result = await service.analyse("What is the current price of Nvidia, Apple and MSFT?")

    assert mock_get_stock_price.await_count == 3

    assert mock_get_stock_price.await_args_list == [
        call("NVDA", price_service),
        call("AAPL", price_service),
        call("MSFT", price_service),
    ]

    assert client.responses.parse.await_count == 2

    second_call = client.responses.parse.await_args_list[1]

    assert second_call.kwargs["input"] == [
        {
            "type": "function_call_output",
            "call_id": "call_1",
            "output": "250.0",
        },
        {
            "type": "function_call_output",
            "call_id": "call_2",
            "output": "260.0",
        },
        {
            "type": "function_call_output",
            "call_id": "call_3",
            "output": "270.0",
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
@patch("portfolio_analyzer.tools.registry.get_stock_price")
async def test_analyse_handles_multiple_stock_price_tool_call_rounds(mock_get_stock_price):
    client = AsyncMock()

    tool_call_1 = Mock()
    tool_call_1.type = "function_call"
    tool_call_1.name = "get_stock_price"
    tool_call_1.arguments = '{"symbol": "NVDA"}'
    tool_call_1.call_id = "call_1"

    tool_call_2 = Mock()
    tool_call_2.type = "function_call"
    tool_call_2.name = "get_stock_price"
    tool_call_2.arguments = '{"symbol": "AAPL"}'
    tool_call_2.call_id = "call_2"

    fake_response_1 = Mock()
    fake_response_1.output = [tool_call_1]
    fake_response_1.id = "response_123"

    fake_response_2 = Mock()
    fake_response_2.output = [tool_call_2]
    fake_response_2.id = "response_234"

    final_response = Mock()
    final_response.output = []
    final_response.output_parsed = PortfolioAnalysis(
        summary="test summary",
        diversification="test diversification",
        risks=["test risk"],
        recommendations=["test recommendation"],
    )

    client.responses.parse.side_effect = [
        fake_response_1,
        fake_response_2,
        final_response,
    ]

    price_service = Mock(spec=PriceService)

    async def get_stock_price_side_effect(symbol, _price_service):
        prices = {
            "NVDA": 250.00,
            "AAPL": 260.00
        }
        return prices[symbol]

    mock_get_stock_price.side_effect = get_stock_price_side_effect

    portfolio_valuator = Mock(spec=PortfolioValuator)
    portfolio_repository = create_autospec(PortfolioRepository)
    portfolio_analytics = Mock(spec=PortfolioAnalytics)

    service = LLMService(client, price_service, portfolio_repository, portfolio_valuator, portfolio_analytics)

    result = await service.analyse("What is the current price of Nvidia and Apple?")

    assert mock_get_stock_price.await_count == 2

    assert mock_get_stock_price.await_args_list == [
        call("NVDA", price_service),
        call("AAPL", price_service)
    ]

    assert client.responses.parse.await_count == 3

    second_call = client.responses.parse.await_args_list[1]
    third_call = client.responses.parse.await_args_list[2]

    assert second_call.kwargs["input"] == [
        {
            "type": "function_call_output",
            "call_id": "call_1",
            "output": "250.0",
        }
    ]

    assert third_call.kwargs["input"] == [
        {
            "type": "function_call_output",
            "call_id": "call_2",
            "output": "260.0",
        }
    ]

    assert second_call.kwargs["previous_response_id"] == "response_123"
    assert third_call.kwargs["previous_response_id"] == "response_234"

    assert result == PortfolioAnalysis(
        summary="test summary",
        diversification="test diversification",
        risks=["test risk"],
        recommendations=["test recommendation"],
    )


@pytest.mark.asyncio
@patch("portfolio_analyzer.tools.registry.get_allocation")
async def test_analyse_handles_allocation_tool_call(mock_get_allocation):
    client = AsyncMock()

    tool_call = Mock()
    tool_call.type = "function_call"
    tool_call.name = "get_allocation"
    tool_call.arguments = '{}'
    tool_call.call_id = "call_123"

    fake_response = Mock()
    fake_response.output = [tool_call]
    fake_response.id = "response_123"

    assert fake_response.output[0].type == "function_call"

    final_response = Mock()
    final_response.output = []
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

    mock_get_allocation.return_value = (
        AllocationResult(symbol="AAPL", weight=0.33),
        AllocationResult(symbol="MSFT", weight=0.66)
    )

    portfolio_valuator = Mock(spec=PortfolioValuator)
    portfolio_repository = create_autospec(PortfolioRepository)
    portfolio_analytics = Mock(spec=PortfolioAnalytics)

    service = LLMService(client, price_service, portfolio_repository, portfolio_valuator, portfolio_analytics)

    result = await service.analyse("What is my portfolio allocation?")

    mock_get_allocation.assert_awaited_once_with(portfolio_repository, portfolio_valuator, portfolio_analytics)

    assert client.responses.parse.await_count == 2

    second_call = client.responses.parse.await_args_list[1]

    expected_allocations = '[{"symbol": "AAPL", "weight": 0.33}, {"symbol": "MSFT", "weight": 0.66}]'

    assert second_call.kwargs["input"] == [
        {
            "type": "function_call_output",
            "call_id": "call_123",
            "output": expected_allocations
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
@patch("portfolio_analyzer.tools.registry.get_allocation")
@patch("portfolio_analyzer.tools.registry.get_stock_price")
async def test_analyse_handles_multiple_tool_types_in_same_response(mock_get_stock_price, mock_get_allocation):
    client = AsyncMock()

    tool_call_1 = Mock()
    tool_call_1.type = "function_call"
    tool_call_1.name = "get_stock_price"
    tool_call_1.arguments = '{"symbol": "AAPL"}'
    tool_call_1.call_id = "call_1"

    tool_call_2 = Mock()
    tool_call_2.type = "function_call"
    tool_call_2.name = "get_stock_price"
    tool_call_2.arguments = '{"symbol": "MSFT"}'
    tool_call_2.call_id = "call_2"

    tool_call_3 = Mock()
    tool_call_3.type = "function_call"
    tool_call_3.name = "get_allocation"
    tool_call_3.arguments = '{}'
    tool_call_3.call_id = "call_3"

    fake_response = Mock()
    fake_response.output = [tool_call_1, tool_call_2, tool_call_3]
    fake_response.id = "response_123"

    final_response = Mock()
    final_response.output = []
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

    async def get_stock_price_side_effect(symbol, _price_service):
        prices = {
            "AAPL": 100.00,
            "MSFT": 200.00,
        }
        return prices[symbol]

    mock_get_stock_price.side_effect = get_stock_price_side_effect
    mock_get_allocation.return_value = (
        AllocationResult(symbol="AAPL", weight=0.33),
        AllocationResult(symbol="MSFT", weight=0.66)
    )

    portfolio_valuator = Mock(spec=PortfolioValuator)
    portfolio_repository = create_autospec(PortfolioRepository)
    portfolio_analytics = Mock(spec=PortfolioAnalytics)

    service = LLMService(client, price_service, portfolio_repository, portfolio_valuator, portfolio_analytics)

    result = await service.analyse("What is the current price of AAPL and MSFT?")

    assert mock_get_stock_price.await_count == 2
    assert mock_get_allocation.await_count == 1

    assert mock_get_stock_price.await_args_list == [
        call("AAPL", price_service),
        call("MSFT", price_service),
    ]

    assert client.responses.parse.await_count == 2

    second_call = client.responses.parse.await_args_list[1]

    expected_allocations = '[{"symbol": "AAPL", "weight": 0.33}, {"symbol": "MSFT", "weight": 0.66}]'

    assert second_call.kwargs["input"] == [
        {
            "type": "function_call_output",
            "call_id": "call_1",
            "output": "100.0",
        },
        {
            "type": "function_call_output",
            "call_id": "call_2",
            "output": "200.0",
        },
        {
            "type": "function_call_output",
            "call_id": "call_3",
            "output": expected_allocations,
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
@patch("portfolio_analyzer.tools.registry.get_allocation")
@patch("portfolio_analyzer.tools.registry.get_stock_price")
async def test_analyse_handles_multiple_tool_call_rounds(mock_get_stock_price, mock_get_allocation):
    client = AsyncMock()

    tool_call_1 = Mock()
    tool_call_1.type = "function_call"
    tool_call_1.name = "get_stock_price"
    tool_call_1.arguments = '{"symbol": "AAPL"}'
    tool_call_1.call_id = "call_1"

    tool_call_2 = Mock()
    tool_call_2.type = "function_call"
    tool_call_2.name = "get_allocation"
    tool_call_2.arguments = '{}'
    tool_call_2.call_id = "call_2"

    fake_response_1 = Mock()
    fake_response_1.output = [tool_call_1]
    fake_response_1.id = "response_123"

    fake_response_2 = Mock()
    fake_response_2.output = [tool_call_2]
    fake_response_2.id = "response_234"

    final_response = Mock()
    final_response.output = []
    final_response.output_parsed = PortfolioAnalysis(
        summary="test summary",
        diversification="test diversification",
        risks=["test risk"],
        recommendations=["test recommendation"],
    )

    client.responses.parse.side_effect = [
        fake_response_1,
        fake_response_2,
        final_response,
    ]

    price_service = Mock(spec=PriceService)

    async def get_stock_price_side_effect(symbol, _price_service):
        prices = {
            "AAPL": 100.00,
            "MSFT": 200.00,
        }
        return prices[symbol]

    mock_get_stock_price.side_effect = get_stock_price_side_effect

    mock_get_allocation.return_value = (
        AllocationResult(symbol="AAPL", weight=0.33),
        AllocationResult(symbol="MSFT", weight=0.66)
    )

    portfolio_valuator = Mock(spec=PortfolioValuator)
    portfolio_repository = create_autospec(PortfolioRepository)
    portfolio_analytics = Mock(spec=PortfolioAnalytics)

    service = LLMService(client, price_service, portfolio_repository, portfolio_valuator, portfolio_analytics)

    result = await service.analyse("What is my portfolio allocation and the current price of Apple and Microsoft?")

    assert mock_get_stock_price.await_count == 1
    assert mock_get_allocation.await_count == 1

    assert mock_get_stock_price.await_args_list == [
        call("AAPL", price_service),
    ]

    assert client.responses.parse.await_count == 3

    second_call = client.responses.parse.await_args_list[1]
    third_call = client.responses.parse.await_args_list[2]

    assert second_call.kwargs["input"] == [
        {
            "type": "function_call_output",
            "call_id": "call_1",
            "output": "100.0",
        }
    ]

    expected_allocations = '[{"symbol": "AAPL", "weight": 0.33}, {"symbol": "MSFT", "weight": 0.66}]'

    assert third_call.kwargs["input"] == [
        {
            "type": "function_call_output",
            "call_id": "call_2",
            "output": expected_allocations,
        }
    ]

    assert second_call.kwargs["previous_response_id"] == "response_123"
    assert third_call.kwargs["previous_response_id"] == "response_234"

    assert result == PortfolioAnalysis(
        summary="test summary",
        diversification="test diversification",
        risks=["test risk"],
        recommendations=["test recommendation"],
    )


def test_serialize_tool_result_returns_json_for_float(llm_service):
    result = llm_service._serialize_tool_result(250.19)

    assert json.loads(result) == 250.19


def test_serialize_tool_result_returns_json_for_tuple_of_pydantic_models(llm_service):
    tool_result = (
        AllocationResult(symbol="AAPL", weight=0.33),
        AllocationResult(symbol="MSFT", weight=0.66),
    )

    result = llm_service._serialize_tool_result(tool_result)

    assert json.loads(result) == [
        {"symbol": "AAPL", "weight": 0.33},
        {"symbol": "MSFT", "weight": 0.66},
    ]


@pytest.mark.asyncio
async def test_analyse_raises_llm_service_error_for_no_structured_output():
    client = AsyncMock()

    fake_response = Mock()
    fake_response.output = []
    fake_response.output_parsed = None

    client.responses.parse.return_value = fake_response

    price_service = Mock(spec=PriceService)
    portfolio_valuator = Mock(spec=PortfolioValuator)
    portfolio_repository = create_autospec(PortfolioRepository)
    portfolio_analytics = Mock(spec=PortfolioAnalytics)

    service = LLMService(client, price_service, portfolio_repository, portfolio_valuator, portfolio_analytics)

    with pytest.raises(LLMServiceError) as excinfo:
        await service.analyse("Analyse my portfolio")

    assert str(excinfo.value) == "LLM returned no structured output."


@pytest.mark.asyncio
async def test_analyse_raises_llm_service_error_for_openai_error():
    client = AsyncMock()

    client.responses.parse.side_effect = OpenAIError("Something went wrong")

    price_service = Mock(spec=PriceService)
    portfolio_valuator = Mock(spec=PortfolioValuator)
    portfolio_repository = create_autospec(PortfolioRepository)
    portfolio_analytics = Mock(spec=PortfolioAnalytics)

    service = LLMService(client, price_service, portfolio_repository, portfolio_valuator, portfolio_analytics)

    with pytest.raises(LLMServiceError) as excinfo:
        await service.analyse("Analyse my portfolio")

    assert str(excinfo.value) == "LLM service error."

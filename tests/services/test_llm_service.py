from unittest.mock import AsyncMock, Mock

import pytest
from openai import OpenAIError

from portfolio_analyzer.exceptions.llm_service import LLMServiceError
from portfolio_analyzer.models.portfolio_analysis import PortfolioAnalysis
from portfolio_analyzer.services.llm_service import LLMService

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
    fake_response.output_parsed = portfolio_analysis

    client.responses.parse.return_value = fake_response

    service = LLMService(client)

    result = await service.analyse("Analyse my portfolio")

    assert result == portfolio_analysis

    client.responses.parse.assert_awaited_once_with(
        text_format=PortfolioAnalysis,
        model="gpt-5.6-luna",
        input="Analyse my portfolio",
    )


@pytest.mark.asyncio
async def test_analyse_raises_llm_service_error_for_no_structured_output():
    client = AsyncMock()

    fake_response = Mock()
    fake_response.output_parsed = None

    client.responses.parse.return_value = fake_response

    service = LLMService(client)

    with pytest.raises(LLMServiceError) as excinfo:
        await service.analyse("Analyse my portfolio")

    assert str(excinfo.value) == "LLM returned no structured output."


@pytest.mark.asyncio
async def test_analyse_raises_llm_service_error_for_openai_error():
    client = AsyncMock()

    client.responses.parse.side_effect = OpenAIError("Something went wrong")

    service = LLMService(client)
    with pytest.raises(LLMServiceError) as excinfo:
        await service.analyse("Analyse my portfolio")

    assert str(excinfo.value) == "LLM service error."

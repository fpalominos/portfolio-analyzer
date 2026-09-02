from unittest.mock import AsyncMock, Mock
from xmlrpc import client

import pytest
from openai import OpenAIError

from portfolio_analyzer.exceptions.llm_service import LLMServiceError
from portfolio_analyzer.services.llm_service import LLMService

# create() is the async operation we await, so it is represented by an AsyncMock.
# The Response returned by create() is a normal object, so a regular Mock is enough.
# The fact that client is an AsyncMock means its methods are automatically mocked as asynchronous operations. So client.responses.create acts as an AsyncMock child
"""
client = AsyncMock()
       ↓
responses.create() = AsyncMock
       ↓ await
fake_response = Mock
       ↓
output_text
"""


@pytest.mark.asyncio
async def test_analyse_returns_response_text():
    client = AsyncMock()

    fake_response = Mock()
    fake_response.output_text = "This is a portfolio analysis."

    client.responses.create.return_value = fake_response

    service = LLMService(client)

    result = await service.analyse("Analyse my portfolio")

    assert result == "This is a portfolio analysis."

    client.responses.create.assert_awaited_once_with(
        model="gpt-5.6-luna",
        input="Analyse my portfolio",
    )


@pytest.mark.asyncio
async def test_analyse_raises_llm_service_error():
    client = AsyncMock()

    client.responses.create.side_effect = OpenAIError("Something went wrong")

    service = LLMService(client)
    with pytest.raises(LLMServiceError) as excinfo:
        await service.analyse("Analyse my portfolio")

    assert str(excinfo.value) == "LLM service error."

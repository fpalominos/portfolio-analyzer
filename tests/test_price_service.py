from unittest.mock import AsyncMock

import httpx
import pytest

from portfolio_analyzer.exceptions.price_service import (
    InvalidApiKeyError,
    InvalidSymbolError,
    PriceServiceError,
)
from portfolio_analyzer.models.finnhub_quote import FinnhubQuote
from portfolio_analyzer.services.price_service import PriceService


@pytest.mark.asyncio
async def test_get_quote_returns_quote():
    client = AsyncMock()

    response = httpx.Response(
        status_code=200,
        json={
            "c": 210.50,
            "d": 1.50,
            "dp": 0.72,
            "h": 212.00,
            "l": 208.00,
            "o": 209.00,
            "pc": 209.00,
            "t": 1234567890,
        },
        request=httpx.Request("GET", "https://finnhub.io/api/v1/quote"),
    )

    client.get.return_value = response

    service = PriceService(
        client=client,
        api_key="test-key",
    )

    quote: FinnhubQuote = await service.get_quote("AAPL")

    assert isinstance(quote, FinnhubQuote)
    assert quote.current_price == 210.50

    client.get.assert_awaited_once_with(
        "https://finnhub.io/api/v1/quote",
        params={
            "symbol": "AAPL",
            "token": "test-key",
        },
    )


@pytest.mark.asyncio
async def test_get_price_returns_float():
    client = AsyncMock()
    response = httpx.Response(
        status_code=200,
        json={"c": 100.0, "h": 101, "l": 99, "o": 100, "pc": 99},
        request=httpx.Request("GET", "https://finnhub.io/api/v1/quote"),
    )
    client.get.return_value = response

    service = PriceService(client=client, api_key="k")
    price = await service.get_price("MSFT")
    assert isinstance(price, float)
    assert price == 100.0


@pytest.mark.asyncio
async def test_get_quote_raises_invalid_symbol_when_price_zero():
    client = AsyncMock()
    # Finnhub returns a quote with current price 0 for unknown symbols
    response = httpx.Response(
        status_code=200,
        json={"c": 0.0, "h": 0.0, "l": 0.0, "o": 0.0, "pc": 0.0},
        request=httpx.Request("GET", "https://finnhub.io/api/v1/quote"),
    )
    client.get.return_value = response

    service = PriceService(client=client, api_key="k")
    with pytest.raises(InvalidSymbolError):
        await service.get_quote("UNKNOWN")


@pytest.mark.asyncio
async def test_get_quote_raises_invalid_api_key_on_401():
    client = AsyncMock()

    # Return a 401 response; response.raise_for_status() will raise HTTPStatusError
    req = httpx.Request("GET", "https://finnhub.io/api/v1/quote")
    resp = httpx.Response(status_code=401, json={"error": "Unauthorized"}, request=req)
    client.get.return_value = resp

    service = PriceService(client=client, api_key="bad-key")
    with pytest.raises(InvalidApiKeyError):
        await service.get_quote("AAPL")


@pytest.mark.asyncio
async def test_get_quote_raises_price_service_error_on_http_500():
    client = AsyncMock()

    # Return a 500 response; response.raise_for_status() will raise HTTPStatusError
    req = httpx.Request("GET", "https://finnhub.io/api/v1/quote")
    resp = httpx.Response(status_code=500, json={"error": "Server error"}, request=req)
    client.get.return_value = resp

    service = PriceService(client=client, api_key="k")
    with pytest.raises(PriceServiceError) as excinfo:
        await service.get_quote("AAPL")

    assert "Finnhub return HTTP 500" in str(excinfo.value)


@pytest.mark.asyncio
async def test_get_quote_raises_price_service_error_on_request_error():
    client = AsyncMock()
    # Simulate a network/request error when calling client.get
    client.get.side_effect = httpx.RequestError(
        "connection failed",
        request=httpx.Request("GET", "https://finnhub.io/api/v1/quote"),
    )

    service = PriceService(client=client, api_key="k")
    with pytest.raises(PriceServiceError) as excinfo:
        await service.get_quote("AAPL")

    assert "Could not connect to Finnhub." in str(excinfo.value)


def test_parse_quote_raises_invalid_api_key_for_error_field():
    # _parse_quote is a static method; if the data contains "error": "Invalid API key."
    # it should raise InvalidApiKeyError
    with pytest.raises(InvalidApiKeyError):
        PriceService._parse_quote({"error": "Invalid API key."})


def test_parse_quote_raises_price_service_error_for_other_error_field():
    with pytest.raises(PriceServiceError) as excinfo:
        PriceService._parse_quote({"error": "Some other error occurred"})

    assert "Some other error occurred" in str(excinfo.value)


def test_parse_quote_raises_price_service_error_on_validation_error():
    # Provide malformed/empty data so model validation fails
    with pytest.raises(PriceServiceError) as excinfo:
        PriceService._parse_quote({})

    assert "Unexpected response from Finnhub." in str(excinfo.value)

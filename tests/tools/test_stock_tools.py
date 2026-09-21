from unittest.mock import AsyncMock, Mock

import pytest

from portfolio_analyzer.exceptions.price_service import InvalidSymbolError, PriceServiceError
from portfolio_analyzer.models.finnhub_quote import FinnhubQuote
from portfolio_analyzer.services.price_service import PriceService
from portfolio_analyzer.tools.stock_tools import get_stock_price


@pytest.mark.asyncio
async def test_get_stock_price_returns_the_expected_price():
    price_service = Mock(spec=PriceService)

    price_service.get_quote = AsyncMock(
        return_value=FinnhubQuote(
            c=210.50,
            h=212.00,
            l=208.00,
            o=209.00,
            pc=209.00
        )
    )

    stock_price = await get_stock_price("AAPL", price_service)

    assert stock_price == 210.50
    price_service.get_quote.assert_awaited_once_with(symbol="AAPL")


@pytest.mark.asyncio
async def test_get_stock_price_fails_when_symbol_is_invalid():
    price_service = Mock(spec=PriceService)

    price_service.get_quote = AsyncMock()
    price_service.get_quote.side_effect = PriceServiceError(
        "Unable to retrieve price"
    )

    with pytest.raises(PriceServiceError) as excinfo:
        await get_stock_price("AAPL", price_service)

    assert str(excinfo.value) == "Unable to retrieve price"

    # diff syntax, more concise
    # price_service.get_quote = AsyncMock(side_effect=PriceServiceError("Unable to retrieve price"))
    # with pytest.raises(PriceServiceError, match="Unable to retrieve price"):
    #     await get_stock_price("UNKNOWN", price_service)

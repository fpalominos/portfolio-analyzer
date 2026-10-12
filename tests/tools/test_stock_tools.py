from unittest.mock import AsyncMock, Mock

import pytest

from portfolio_analyzer.analytics.portfolio_analytics import PortfolioAnalytics
from portfolio_analyzer.domain.stock import Stock
from portfolio_analyzer.domain.valued_position import ValuedPosition
from portfolio_analyzer.exceptions.portfolio import PortfolioNotFoundError
from portfolio_analyzer.exceptions.price_service import PriceServiceError
from portfolio_analyzer.models.allocation_result import AllocationResult
from portfolio_analyzer.models.finnhub_quote import FinnhubQuote
from portfolio_analyzer.services.portfolio_valuator import PortfolioValuator
from portfolio_analyzer.services.price_service import PriceService
from portfolio_analyzer.tools.stock_tools import get_stock_price, get_allocation


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


@pytest.mark.asyncio
async def test_get_allocation_returns_the_expected_allocation_result(portfolio, portfolio_repository):
    portfolio_valuator = Mock(spec=PortfolioValuator)
    portfolio_analytics = PortfolioAnalytics()

    nvidia_stock = Stock("NVDA", 10)
    msft_stock = Stock("MSFT", 20)

    portfolio_repository.save(
        portfolio
        .add_position(nvidia_stock)
        .add_position(msft_stock))

    saved_portfolio = portfolio_repository.get()

    portfolio_valuator.value_positions.return_value = (
        ValuedPosition(
            nvidia_stock,
            10.0,
        ),
        ValuedPosition(
            msft_stock,
            20.0,
        ),

    )

    result = await get_allocation(portfolio_repository, portfolio_valuator, portfolio_analytics)

    expected: tuple[AllocationResult, ...] = (
        AllocationResult(symbol="NVDA", weight=0.2),
        AllocationResult(symbol="MSFT", weight=0.8)
    )

    portfolio_valuator.value_positions.assert_awaited_once_with(
        saved_portfolio
    )

    assert result == expected


@pytest.mark.asyncio
async def test_get_allocation_raises_when_portfolio_is_missing(portfolio_repository):
    portfolio_valuator = Mock(spec=PortfolioValuator)

    with pytest.raises(PortfolioNotFoundError) as excinfo:
        await get_allocation(portfolio_repository, portfolio_valuator, PortfolioAnalytics())

    assert str(excinfo.value) == "Portfolio not found"

    portfolio_valuator.value_positions.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_allocation_propagates_valuation_error(portfolio, portfolio_repository):
    price_service = Mock(spec=PriceService)

    price_service.get_price.side_effect = PriceServiceError(
        "Unable to retrieve price"
    )

    portfolio_valuator = PortfolioValuator(price_service)

    nvidia_stock = Stock("NVDA", 10)
    msft_stock = Stock("MSFT", 20)

    portfolio_repository.save(
        portfolio
        .add_position(nvidia_stock)
        .add_position(msft_stock))

    with pytest.raises(PriceServiceError) as excinfo:
        await get_allocation(portfolio_repository, portfolio_valuator, PortfolioAnalytics())

    assert str(excinfo.value) == "Unable to retrieve price"

    price_service.get_price.assert_awaited()

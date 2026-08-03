from portfolio_analyzer.domain.portfolio import Portfolio
from portfolio_analyzer.analytics.portfolio_analytics import PortfolioAnalytics
from portfolio_analyzer.domain.portfolio_valuator import PortfolioValuator
from portfolio_analyzer.services.price_service import PriceService
from portfolio_analyzer.domain.stock import Stock
from portfolio_analyzer.domain.valued_position import ValuedPosition


async def test_total_value():
    price_service = PriceService()
    valuator = PortfolioValuator(price_service)

    portfolio = (
        Portfolio()
        .add_position(Stock("AAPL", 10))
        .add_position(Stock("MSFT", 5))
    )

    positions = await valuator.value_positions(portfolio)

    assert PortfolioAnalytics.total_value(positions) == 10 * 100 + 5 * 200


async def test_largest_position():
    price_service = PriceService()
    valuator = PortfolioValuator(price_service)

    portfolio = (
        Portfolio()
        .add_position(Stock("AAPL", 10))
        .add_position(Stock("MSFT", 5))
    )

    positions = await valuator.value_positions(portfolio)

    assert PortfolioAnalytics.largest_position(positions) == ValuedPosition(Stock("MSFT", 5), 5000)


async def test_largest_position_empty():
    portfolio = Portfolio()
    price_service = PriceService()
    valuator = PortfolioValuator(price_service)
    portfolio_analytics = PortfolioAnalytics

    positions = await valuator.value_positions(portfolio)

    assert portfolio_analytics.largest_position(positions) is None

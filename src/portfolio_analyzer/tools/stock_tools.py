from portfolio_analyzer.analytics.portfolio_analytics import PortfolioAnalytics
from portfolio_analyzer.domain.allocation import Allocation
from portfolio_analyzer.repositories.portfolio_repository import PortfolioRepository
from portfolio_analyzer.services.portfolio_valuator import PortfolioValuator
from portfolio_analyzer.services.price_service import PriceService


async def get_stock_price(
        symbol: str,
        price_service: PriceService) -> float:
    quote = await price_service.get_quote(symbol=symbol)
    return quote.current_price


async def get_allocation(
        portfolio_repository: PortfolioRepository,
        portfolio_valuator: PortfolioValuator,
        portfolio_analytics: PortfolioAnalytics
) -> tuple[Allocation, ...]:
    portfolio = portfolio_repository.get()

    if portfolio is None:
        raise ValueError("Portfolio not found")
    valued_positions = await portfolio_valuator.value_positions(portfolio)
    return portfolio_analytics.allocation(valued_positions)

import asyncio

from config import Settings
import httpx
from portfolio_analyzer.domain.allocation import Allocation
from portfolio_analyzer.domain.portfolio import Portfolio
from portfolio_analyzer.analytics.portfolio_analytics import PortfolioAnalytics
from portfolio_analyzer.domain.portfolio_valuator import PortfolioValuator
from portfolio_analyzer.services.price_service import PriceService
from portfolio_analyzer.domain.stock import Stock
from portfolio_analyzer.domain.valued_position import ValuedPosition


async def main() -> None:
    portfolio = (
        Portfolio()
        .add_position(Stock("AAPL", 10))
        .add_position(Stock("MSFT", 5))
        .add_position(Stock("NVDA", 3))
    )

    settings = Settings()
    print("Loaded settings:", settings.model_dump())
    client = httpx.AsyncClient(timeout=5)
    finnhub_api_key = settings.finnhub_api_key

    async with client as client:
        service: PriceService = PriceService(client, finnhub_api_key)
        valuator: PortfolioValuator = PortfolioValuator(service)
        positions: tuple[ValuedPosition, ...] = await valuator.value_positions(portfolio)

        print("Portfolio Summary")
        print("-----------------")
        total_value: float = PortfolioAnalytics.total_value(positions)
        print(f"Total value: {total_value:.2f}")

        largest_position: ValuedPosition | None = PortfolioAnalytics.largest_position(positions)

        if largest_position:
            print(f"Largest position: {largest_position}. Market value: {largest_position.market_value:.2f}")

        print("\nAllocation:")

        allocation: tuple[Allocation, ...] = PortfolioAnalytics.allocation(positions)

        formatted_allocation = tuple(
            (allocated.position.stock.symbol, f"{allocated.percentage * 100:.2f}%")
            for allocated in allocation)

        if allocation:
            print(f"Allocation: {formatted_allocation}")


if __name__ == "__main__":
    asyncio.run(main())

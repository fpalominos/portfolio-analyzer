import asyncio

from portfolio_analyzer.allocation import Allocation
from portfolio_analyzer.portfolio import Portfolio
from portfolio_analyzer.portfolio_analytics import PortfolioAnalytics
from portfolio_analyzer.portfolio_valuator import PortfolioValuator
from portfolio_analyzer.price_service import PriceService
from portfolio_analyzer.stock import Stock
from portfolio_analyzer.valued_position import ValuedPosition


async def main() -> None:
    portfolio = (
        Portfolio()
        .add_position(Stock("AAPL", 10))
        .add_position(Stock("MSFT", 5))
        .add_position(Stock("NVDA", 3))
    )

    service: PriceService = PriceService()
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

from fastapi import FastAPI

from portfolio_analyzer.api.exceptions import (
    invalid_symbol_exception_handler,
    price_service_exception_handler, portfolio_not_found_exception_handler,
)
from portfolio_analyzer.api.routes import router
from portfolio_analyzer.exceptions.price_service import (
    InvalidSymbolError,
    PriceServiceError,
)

from portfolio_analyzer.exceptions.portfolio import PortfolioNotFoundError

app = FastAPI()

app.include_router(router)

app.add_exception_handler(
    PriceServiceError,
    price_service_exception_handler,
)

app.add_exception_handler(
    InvalidSymbolError,
    invalid_symbol_exception_handler,
)

app.add_exception_handler(
    PortfolioNotFoundError,
    portfolio_not_found_exception_handler,
)

# async def main() -> None:
#     portfolio = (
#         Portfolio()
#         .add_position(Stock("AAPL", 10))
#         .add_position(Stock("MSFT", 5))
#         .add_position(Stock("NVDA", 3))
#     )
#
#     settings = Settings()
#     print("Loaded settings:", settings.model_dump())
#     client = httpx.AsyncClient(timeout=5)
#     finnhub_api_key = settings.finnhub_api_key
#
#     async with client as client:
#         service: PriceService = PriceService(client, finnhub_api_key)
#         valuator: PortfolioValuator = PortfolioValuator(service)
#         positions: tuple[ValuedPosition, ...] = await valuator.value_positions(portfolio)
#
#         print("Portfolio Summary")
#         print("-----------------")
#         total_value: float = PortfolioAnalytics.total_value(positions)
#         print(f"Total value: {total_value:.2f}")
#
#         largest_position: ValuedPosition | None = PortfolioAnalytics.largest_position(positions)
#
#         if largest_position:
#             print(f"Largest position: {largest_position}. Market value: {largest_position.market_value:.2f}")
#
#         print("\nAllocation:")
#
#         allocation: tuple[Allocation, ...] = PortfolioAnalytics.allocation(positions)
#
#         formatted_allocation = tuple(
#             (allocated.position.stock.symbol, f"{allocated.percentage * 100:.2f}%")
#             for allocated in allocation)
#
#         if allocation:
#             print(f"Allocation: {formatted_allocation}")
#
#
#
#
# if __name__ == "__main__":
#     app = FastAPI()
#     asyncio.run(main())

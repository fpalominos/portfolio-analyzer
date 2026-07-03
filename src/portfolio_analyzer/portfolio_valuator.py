import asyncio

from portfolio import Portfolio
from portfolio_analyzer.price_service import PriceService
from stock import Stock


class PortfolioValuator:

    def __init__(self, price_service: PriceService) -> None:
        self.price_service = price_service

    async def value(self, portfolio: Portfolio) -> float:
        tasks = [
            self.price_service.get_price(stock.symbol)
            for stock in portfolio.positions
        ]

        prices = await asyncio.gather(*tasks)

        return sum(
            stock.shares * price
            for stock, price in zip(portfolio.positions, prices)
        )


async def main():
    service = PriceService()
    valuator = PortfolioValuator(service)
    portfolio = (
        Portfolio()
        .add_position(Stock("AAPL", 10))
        .add_position(Stock("MSFT", 10))
    )

    value = await valuator.value(portfolio)
    print(value)


if __name__ == "__main__":
    asyncio.run(main())

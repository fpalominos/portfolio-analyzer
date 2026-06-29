import asyncio

from portfolio import Portfolio
from portfolio_analyzer.price_service import PriceService
from stock import Stock

class PortfolioValuator:

    def __init__(self, price_service: PriceService) -> None:
        self.price_service = price_service

    async def value(self, portfolio: Portfolio) -> float:
        total = 0.0

        for stock in portfolio.positions:
            price = await self.price_service.get_price(stock.symbol)
            total += stock.shares * price

        return total

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

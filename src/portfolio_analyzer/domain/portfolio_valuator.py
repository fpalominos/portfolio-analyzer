import asyncio

from portfolio_analyzer.domain.portfolio import Portfolio
from portfolio_analyzer.services.price_service import PriceService
from portfolio_analyzer.domain.valued_position import ValuedPosition


class PortfolioValuator:

    def __init__(self, price_service: PriceService) -> None:
        self.price_service = price_service

    async def value_positions(self, portfolio: Portfolio) -> tuple[ValuedPosition, ...]:
        tasks = [
            self.price_service.get_price(stock.symbol)
            for stock in portfolio.positions
        ]

        prices = await asyncio.gather(*tasks)

        return (
            tuple(
                ValuedPosition(stock, price)
                for stock, price in zip(
                    portfolio.positions, prices
                )
            )
        )

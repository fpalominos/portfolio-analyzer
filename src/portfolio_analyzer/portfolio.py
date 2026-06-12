from portfolio_analyzer.stock import Stock
from dataclasses import dataclass


@dataclass(frozen=True)
class Portfolio:
    positions: tuple[Stock, ...] = ()

    def add_position(self, stock: Stock) -> "Portfolio":
        return Portfolio(
            positions=self.positions + (stock,)
        )

    def total_value(self) -> float:
        return sum(
            stock.market_value() for stock in self.positions
        )

    def largest_position(self) -> Stock | None:
        return max(
            self.positions,
            key=lambda p: p.market_value(),
            default=None
        )

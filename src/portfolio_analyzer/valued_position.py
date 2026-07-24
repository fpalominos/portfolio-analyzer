from attr import dataclass

from portfolio_analyzer.stock import Stock


@dataclass(frozen=True)
class ValuedPosition:
    stock: Stock
    current_price: float

    @property
    def market_value(self) -> float:
        return self.stock.shares * self.current_price

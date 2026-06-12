from dataclasses import dataclass


@dataclass(frozen=True)
class Stock:
    symbol: str
    shares: int
    price: float

    def market_value(self) -> float:
        return self.shares * self.price

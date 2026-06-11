from dataclasses import dataclass


@dataclass
class Stock:
    symbol: str
    shares: int
    price: float

    def market_value(self) -> float:
        return self.shares * self.price

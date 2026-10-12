from dataclasses import dataclass
from typing import Self

from portfolio_analyzer.domain.stock import Stock


@dataclass(frozen=True)
class Portfolio:
    positions: tuple[Stock, ...] = ()

    def add_position(self, stock: Stock) -> Self:
        return type(self)(
            positions=self.positions + (stock,)
        )

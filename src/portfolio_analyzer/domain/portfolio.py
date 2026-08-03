from dataclasses import dataclass

from portfolio_analyzer.domain.stock import Stock


@dataclass(frozen=True)
class Portfolio:
    positions: tuple[Stock, ...] = ()

    def add_position(self, stock: Stock) -> "Portfolio":
        return Portfolio(
            positions=self.positions + (stock,)
        )

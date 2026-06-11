from portfolio_analyzer.stock import Stock


class Portfolio:
    def __init__(self) -> None:
        self.positions: list[Stock] = []

    def add_position(self, stock: Stock) -> None:
        return self.positions.append(stock)

    def total_value(self) -> float:
        return sum(position.market_value() for position in self.positions)

    def largest_position(self) -> Stock | None:
        if not self.positions:
            return None
        return max(self.positions, key=lambda p: p.market_value())

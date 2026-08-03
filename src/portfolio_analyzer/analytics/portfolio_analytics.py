from portfolio_analyzer.domain.allocation import Allocation
from portfolio_analyzer.domain.valued_position import ValuedPosition


class PortfolioAnalytics:

    @staticmethod
    def total_value(positions: tuple[ValuedPosition, ...]) -> float:
        return sum(
            position.market_value
            for position in positions
        )

    @staticmethod
    def largest_position(positions: tuple[ValuedPosition, ...]):
        return max(positions,
                   key=lambda position: position.market_value,
                   default=None
                   )

    @staticmethod
    def allocation(positions: tuple[ValuedPosition, ...]) -> tuple[Allocation, ...]:

        total: float = PortfolioAnalytics.total_value(positions)

        if total == 0:
            return ()
        else:
            return tuple(
                Allocation(position, position.market_value / total)
                for position in positions
            )

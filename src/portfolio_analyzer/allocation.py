from attr import dataclass

from portfolio_analyzer.valued_position import ValuedPosition

@dataclass(frozen=True)
class Allocation:
    position: ValuedPosition
    percentage: float

from attr import dataclass

from portfolio_analyzer.domain.valued_position import ValuedPosition

@dataclass(frozen=True)
class Allocation:
    position: ValuedPosition
    percentage: float

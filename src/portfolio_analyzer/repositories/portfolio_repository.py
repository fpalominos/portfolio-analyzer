from typing import Protocol
from portfolio_analyzer.domain.portfolio import Portfolio

class PortfolioRepository(Protocol):

    def save(self, portfolio: Portfolio) -> None:
        ...

    def get(self) -> Portfolio | None:
        ...
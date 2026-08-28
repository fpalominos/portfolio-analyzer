from portfolio_analyzer.domain.portfolio import Portfolio

# This repository stores a single portfolio.
# Saving a new portfolio replaces the existing one.
# A multi-user implementation would use a portfolio/user ID as the key.
class InMemoryPortfolioRepository:

    def __init__(self):
        self.portfolio: Portfolio | None = None

    def save(self, portfolio: Portfolio) -> None:
        self.portfolio = portfolio

    def get(self) -> Portfolio | None:
        return self.portfolio

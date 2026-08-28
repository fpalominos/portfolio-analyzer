import pytest

from portfolio_analyzer.domain.portfolio import Portfolio
from portfolio_analyzer.domain.stock import Stock
from portfolio_analyzer.repositories.in_memory_portfolio_repository import InMemoryPortfolioRepository

@pytest.fixture
def portfolio_repository():
    return InMemoryPortfolioRepository()

@pytest.fixture
def portfolio():
    return Portfolio().add_position(Stock("AAPL", 10))


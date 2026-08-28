from portfolio_analyzer.domain.portfolio import Portfolio
from portfolio_analyzer.domain.stock import Stock
from portfolio_analyzer.repositories.in_memory_portfolio_repository import InMemoryPortfolioRepository
from conftest import portfolio_repository


def test_get_returns_none_when_no_portfolio_has_been_saved():
    repository = InMemoryPortfolioRepository()
    portfolio = repository.get()

    assert portfolio is None


def test_save_stores_portfolio():
    repository = InMemoryPortfolioRepository()
    portfolio = (Portfolio()
                 .add_position(Stock("AAPL", 10))
                 .add_position(Stock("MSFT", 5))
                 .add_position(Stock("NVDA", 3))
                 )
    repository.save(portfolio)

    assert repository.get() == portfolio


def test_save_replaces_existing_portfolio():
    repository = InMemoryPortfolioRepository()
    portfolio1 = (Portfolio()
                  .add_position(Stock("AAPL", 10))
                  .add_position(Stock("MSFT", 5))
                  .add_position(Stock("NVDA", 3))
                  )
    portfolio2 = Portfolio().add_position(Stock("AAPL", 10))
    repository.save(portfolio1)
    repository.save(portfolio2)

    assert repository.get() == portfolio2

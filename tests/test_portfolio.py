from portfolio_analyzer.stock import Stock
from portfolio_analyzer.portfolio import Portfolio


def test_total_value():
    portfolio = Portfolio()

    portfolio = portfolio.add_position(Stock("AAPL", 10, 100))
    portfolio = portfolio.add_position(Stock("MSFT", 5, 200))

    assert portfolio.total_value() == 10 * 100 + 5 * 200


def test_largest_position():
    portfolio = Portfolio()

    a = Stock("AAPL", 10, 100)  # 1000
    b = Stock("MSFT", 5, 300)  # 1500

    portfolio = portfolio.add_position(a)
    portfolio = portfolio.add_position(b)

    assert portfolio.largest_position() == b


def test_largest_position_empty():
    portfolio = Portfolio()

    assert portfolio.largest_position() is None

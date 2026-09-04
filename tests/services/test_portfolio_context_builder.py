from textwrap import dedent

from portfolio_analyzer.domain.portfolio import Portfolio
from portfolio_analyzer.domain.stock import Stock
from portfolio_analyzer.services.portfolio_context_builder import portfolio_to_context


def test_portfolio_to_context_returns_the_expected_result():
    portfolio = (Portfolio()
                 .add_position(stock=Stock("AAPL", 1))
                 .add_position(stock=Stock("NVDA", 2))
                 )

    result = dedent("""\
    AAPL: 1 shares
    NVDA: 2 shares""")

    assert portfolio_to_context(portfolio) == result


def test_portfolio_to_context_with_single_position():
    portfolio = Portfolio().add_position(Stock("AAPL", 1))

    expected = "AAPL: 1 shares"

    assert portfolio_to_context(portfolio) == expected


def test_portfolio_to_context_with_empty_portfolio():
    portfolio = Portfolio()

    assert portfolio_to_context(portfolio) == ""

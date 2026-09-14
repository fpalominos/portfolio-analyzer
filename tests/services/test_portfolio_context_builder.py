from textwrap import dedent

from portfolio_analyzer.domain.allocation import Allocation
from portfolio_analyzer.domain.stock import Stock
from portfolio_analyzer.domain.valued_position import ValuedPosition
from portfolio_analyzer.services.portfolio_context_builder import portfolio_to_context


def test_portfolio_to_context_returns_the_expected_result():
    allocations: tuple[Allocation, ...] = (
        Allocation(position=ValuedPosition(stock=Stock("AAPL", 10), current_price=210.00), percentage=10.0),
        Allocation(position=ValuedPosition(stock=Stock("NVDA", 2), current_price=170.00), percentage=90.0),
    )

    expected_context = dedent("""\
    AAPL: 10 shares, current price: $210.00, market value: $2100.00, allocation: 10.00%
    NVDA: 2 shares, current price: $170.00, market value: $340.00, allocation: 90.00%""")

    actual_context = portfolio_to_context(allocations)

    assert actual_context == expected_context


def test_portfolio_to_context_with_single_position():
    allocations: tuple[Allocation, ...] = (
        Allocation(position=ValuedPosition(stock=Stock("AAPL", 10), current_price=210.00), percentage=100.0),
    )

    expected_context = "AAPL: 10 shares, current price: $210.00, market value: $2100.00, allocation: 100.00%"

    actual_context = portfolio_to_context(allocations)

    assert actual_context == expected_context


def test_portfolio_to_context_with_empty_portfolio():
    assert portfolio_to_context(()) == ""

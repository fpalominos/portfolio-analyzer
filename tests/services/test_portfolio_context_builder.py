from textwrap import dedent

from portfolio_analyzer.analytics.portfolio_analytics import PortfolioAnalytics
from portfolio_analyzer.domain.allocation import Allocation
from portfolio_analyzer.domain.stock import Stock
from portfolio_analyzer.domain.valued_position import ValuedPosition
from portfolio_analyzer.services.portfolio_context_builder import portfolio_to_context


def test_portfolio_to_context_returns_the_expected_result():
    allocations: tuple[Allocation, ...] = (
        Allocation(position=ValuedPosition(stock=Stock("AAPL", 10), current_price=210.00), weight=0.10),
        Allocation(position=ValuedPosition(stock=Stock("NVDA", 2), current_price=170.00), weight=0.90),
    )

    total_value = PortfolioAnalytics.total_value(tuple(allocation.position for allocation in allocations))

    expected_context = dedent("""\
    Total Value: $2440.00
    
    AAPL: 10 shares, current price: $210.00, market value: $2100.00, allocation: 10.00%
    NVDA: 2 shares, current price: $170.00, market value: $340.00, allocation: 90.00%""")

    actual_context = portfolio_to_context(allocations, total_value)

    assert actual_context == expected_context


def test_portfolio_to_context_with_single_position():
    allocations: tuple[Allocation, ...] = (
        Allocation(position=ValuedPosition(stock=Stock("AAPL", 10), current_price=210.00), weight=1.0),
    )

    expected_context = "Total Value: $2100.00\n\nAAPL: 10 shares, current price: $210.00, market value: $2100.00, allocation: 100.00%"

    total_value = PortfolioAnalytics.total_value(
        tuple(allocation.position for allocation in allocations)
    )

    actual_context = portfolio_to_context(allocations, total_value)

    assert actual_context == expected_context


def test_portfolio_to_context_with_empty_portfolio():
    assert portfolio_to_context((), 0) == "Total Value: $0.00"

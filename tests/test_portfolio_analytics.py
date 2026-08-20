from portfolio_analyzer.analytics.portfolio_analytics import PortfolioAnalytics
from portfolio_analyzer.domain.allocation import Allocation
from portfolio_analyzer.domain.valued_position import ValuedPosition
from portfolio_analyzer.domain.stock import Stock


def test_total_value_returns_sum_of_market_values():
    positions: tuple[ValuedPosition, ValuedPosition] = (
        ValuedPosition(Stock("AAPL", 10), 100.0),
        ValuedPosition(Stock("MSFT", 10), 200.0)
    )

    assert PortfolioAnalytics.total_value(positions) == 3000.0


def test_largest_position_returns_highest_value():
    positions: tuple[ValuedPosition, ValuedPosition] = (
        ValuedPosition(Stock("AAPL", 10), 100.0),
        ValuedPosition(Stock("MSFT", 10), 200.0)
    )

    assert PortfolioAnalytics.largest_position(positions) == ValuedPosition(Stock("MSFT", 10), 200.0)


def test_allocation_returns_expected_allocation():
    positions: tuple[ValuedPosition, ValuedPosition] = (
        ValuedPosition(Stock("AAPL", 10), 100.0),
        ValuedPosition(Stock("MSFT", 10), 200.0)
    )

    assert PortfolioAnalytics.allocation(positions) == (
        Allocation(ValuedPosition(Stock("AAPL", 10), 100.0), 0.3333333333333333),
        Allocation(ValuedPosition(Stock("MSFT", 10), 200.0), 0.6666666666666666)
    )

def test_allocation_with_zero_total_returns_empty():
    assert PortfolioAnalytics.allocation(()) == ()
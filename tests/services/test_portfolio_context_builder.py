from textwrap import dedent

from portfolio_analyzer.domain.stock import Stock
from portfolio_analyzer.domain.valued_position import ValuedPosition
from portfolio_analyzer.services.portfolio_context_builder import portfolio_to_context


def test_portfolio_to_context_returns_the_expected_result():
    positions: tuple[ValuedPosition, ...] = (
        ValuedPosition(
            stock=Stock("AAPL", 10), current_price=210.00,
        ),
        ValuedPosition(
            stock=Stock("NVDA", 2), current_price=170.00,
        )
    )

    expected_context = dedent("""\
    AAPL: 10 shares, current price: $210.00, market value: $2100.00
    NVDA: 2 shares, current price: $170.00, market value: $340.00""")

    actual_context = portfolio_to_context(positions)

    assert actual_context == expected_context


def test_portfolio_to_context_with_single_position():
    positions: tuple[ValuedPosition, ...] = (
        ValuedPosition(
            stock=Stock("AAPL", 10), current_price=210.00,
        ),
    )

    expected_context = "AAPL: 10 shares, current price: $210.00, market value: $2100.00"

    actual_context = portfolio_to_context(positions)

    assert actual_context == expected_context


def test_portfolio_to_context_with_empty_portfolio():
    assert portfolio_to_context(()) == ""

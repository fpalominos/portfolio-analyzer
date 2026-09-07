from portfolio_analyzer.domain.valued_position import ValuedPosition


def portfolio_to_context(positions: tuple[ValuedPosition, ...]) -> str:
    return "\n".join(
        f"{position.stock.symbol
        }: {position.stock.shares} shares, current price: ${position.current_price:.2f}, market value: ${position.market_value:.2f}"
        for position in positions
    )

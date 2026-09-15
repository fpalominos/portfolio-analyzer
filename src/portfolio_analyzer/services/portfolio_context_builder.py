from portfolio_analyzer.domain.allocation import Allocation


def portfolio_to_context(allocations: tuple[Allocation, ...], total_value: float) -> str:

    total_value_context = f"Total Value: ${total_value:.2f}"

    positions_context = "\n".join(
        f"{allocation.position.stock.symbol}: {allocation.position.stock.shares} shares, current price: ${allocation.position.current_price:.2f}, market value: ${allocation.position.market_value:.2f}, allocation: {allocation.percentage:.2f}%"
        for allocation in allocations
    )

    if not allocations:
        return total_value_context
    else:
        return f"{total_value_context}\n\n{positions_context}"


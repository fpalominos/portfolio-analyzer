from portfolio_analyzer.domain.allocation import Allocation


def portfolio_to_context(allocations: tuple[Allocation, ...]) -> str:
    return "\n".join(
        f"{allocation.position.stock.symbol}: {allocation.position.stock.shares} shares, current price: ${allocation.position.current_price:.2f}, market value: ${allocation.position.market_value:.2f}, allocation: {allocation.percentage:.2f}%"
        for allocation in allocations
    )

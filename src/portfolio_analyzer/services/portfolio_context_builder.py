from portfolio_analyzer.domain.portfolio import Portfolio
from portfolio_analyzer.domain.stock import Stock


def portfolio_to_context(portfolio: Portfolio) -> str:
    return "\n".join(f"{position.symbol}: {position.shares} shares"
                   for position in portfolio.positions
                   )


if __name__ == "__main__":
    port = (Portfolio()
            .add_position(stock=Stock("APPL", 1))
            .add_position(stock=Stock("NVDA", 2))
            )

    print(portfolio_to_context(port))

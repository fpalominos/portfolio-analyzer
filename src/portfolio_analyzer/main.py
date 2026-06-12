from portfolio_analyzer.portfolio import Portfolio
from portfolio_analyzer.stock import Stock


def main() -> None:
    portfolio = Portfolio()

    portfolio = portfolio.add_position(Stock("AAPL", 10, 100))
    portfolio = portfolio.add_position(Stock("MSFT", 5, 200))
    portfolio = portfolio.add_position(Stock("NVDA", 3, 300))

    print("Portfolio Summary")
    print("-----------------")

    print(f"Total value: {portfolio.total_value():.2f}")

    largest = portfolio.largest_position()
    if largest:
        print(f"Largest position: {largest.symbol} ({largest.market_value():.2f})")

    print("\nAllocation:")
    total = portfolio.total_value()

    for stock in portfolio.positions:
        pct = (stock.market_value() / total) * 100
        print(f"{stock.symbol}: {pct:.1f}%")


if __name__ == "__main__":
    main()

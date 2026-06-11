from portfolio import Portfolio
from stock import Stock


def main() -> None:
    portfolio = Portfolio()

    portfolio.add_position(
        Stock("NVDA", 10, 180.0)
    )

    portfolio.add_position(
        Stock("MSFT", 5, 520.0)
    )

    print(
        f"Portfolio value: "
        f"${portfolio.total_value():,.2f}"
    )


if __name__ == "__main__":
    main()

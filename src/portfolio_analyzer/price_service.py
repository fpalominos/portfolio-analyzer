class PriceService:
    _PRICES: dict[str, float] = {
        "AAPL": 10,
        "MSFT": 10,
        "NVDA": 10
    }

    async def get_price(self, symbol: str) -> float:
        if symbol not in self._PRICES:
            raise ValueError(f"Unknown symbol: {symbol}")
        return self._PRICES[symbol]

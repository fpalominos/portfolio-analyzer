class PriceService:
    _PRICES: dict[str, float] = {
        "AAPL": 210.0,
        "MSFT": 510.0,
        "NVDA": 170.0
    }

    async def get_price(self, symbol: str) -> float:
        if symbol not in self._PRICES:
            raise ValueError(f"Unknown symbol: {symbol}")
        return self._PRICES[symbol]

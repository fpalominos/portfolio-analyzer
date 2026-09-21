from portfolio_analyzer.services.price_service import PriceService


async def get_stock_price(
        symbol: str,
        price_service: PriceService) -> float:
    quote = await price_service.get_quote(symbol=symbol)
    return quote.current_price

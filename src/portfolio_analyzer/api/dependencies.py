import httpx

from portfolio_analyzer.config import Settings
from portfolio_analyzer.services.portfolio_valuator import PortfolioValuator
from portfolio_analyzer.services.price_service import PriceService


async def get_valuator():
    settings = Settings()

    async with httpx.AsyncClient(timeout=5) as client:
        price_service = PriceService(
            client,
            settings.finnhub_api_key,
        )

        valuator = PortfolioValuator(price_service)

        yield valuator

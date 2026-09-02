import httpx

from portfolio_analyzer.config import Settings
from portfolio_analyzer.repositories.in_memory_portfolio_repository import InMemoryPortfolioRepository
from portfolio_analyzer.repositories.portfolio_repository import PortfolioRepository
from portfolio_analyzer.services.llm_service import LLMService
from portfolio_analyzer.services.portfolio_valuator import PortfolioValuator
from portfolio_analyzer.services.price_service import PriceService
from openai import AsyncOpenAI


async def get_valuator():
    settings = Settings()

    async with httpx.AsyncClient(timeout=5) as client:
        price_service = PriceService(
            client,
            settings.finnhub_api_key,
        )

        valuator = PortfolioValuator(price_service)

        yield valuator


portfolio_repository = InMemoryPortfolioRepository()


def get_portfolio_repository() -> PortfolioRepository:
    return portfolio_repository


def get_llm_service() -> LLMService:
    settings = Settings()

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    return LLMService(client=client)

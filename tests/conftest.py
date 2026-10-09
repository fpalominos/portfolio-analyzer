from unittest.mock import AsyncMock, Mock, create_autospec

import pytest

from portfolio_analyzer.analytics.portfolio_analytics import PortfolioAnalytics
from portfolio_analyzer.domain.portfolio import Portfolio
from portfolio_analyzer.domain.stock import Stock
from portfolio_analyzer.models.portfolio_analysis import PortfolioAnalysis
from portfolio_analyzer.repositories.in_memory_portfolio_repository import InMemoryPortfolioRepository
from portfolio_analyzer.repositories.portfolio_repository import PortfolioRepository
from portfolio_analyzer.services.llm_service import LLMService
from portfolio_analyzer.services.portfolio_valuator import PortfolioValuator
from portfolio_analyzer.services.price_service import PriceService


@pytest.fixture
def portfolio_repository():
    return InMemoryPortfolioRepository()


@pytest.fixture
def portfolio():
    return Portfolio().add_position(Stock("AAPL", 10))


@pytest.fixture
def portfolio_analysis():
    return PortfolioAnalysis(
        summary="test summary",
        diversification="test diversification",
        risks=["test risks1", "test risk 2"],
        recommendations=["recommendation 1", "recommendation 2"]
    )

@pytest.fixture
def llm_service():
    client = AsyncMock()

    fake_response = Mock()
    fake_response.output = []
    fake_response.output_parsed = None

    client.responses.parse.return_value = fake_response

    price_service = Mock(spec=PriceService)
    portfolio_valuator = Mock(spec=PortfolioValuator)
    portfolio_repository = create_autospec(PortfolioRepository)
    portfolio_analytics = Mock(spec=PortfolioAnalytics)

    return LLMService(client, price_service, portfolio_repository, portfolio_valuator, portfolio_analytics)

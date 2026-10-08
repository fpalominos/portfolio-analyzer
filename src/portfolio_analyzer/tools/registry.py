from portfolio_analyzer.analytics.portfolio_analytics import PortfolioAnalytics
from portfolio_analyzer.repositories.portfolio_repository import PortfolioRepository
from portfolio_analyzer.services.portfolio_valuator import PortfolioValuator
from portfolio_analyzer.services.price_service import PriceService
from portfolio_analyzer.tools.stock_tools import get_stock_price, get_allocation


def build_tool_registry(
        price_service: PriceService,
        portfolio_repository: PortfolioRepository,
        portfolio_valuator: PortfolioValuator,
        portfolio_analytics: PortfolioAnalytics,
):
    tool_registry = {
        'get_stock_price': {
            'executor': get_stock_price,
            'dependencies': [price_service],
            'llm_arguments': ["symbol"]
        },
        'get_allocation': {
            'executor': get_allocation,
            'dependencies': [portfolio_repository, portfolio_valuator, portfolio_analytics],
            'llm_arguments': []
        },
    }

    return tool_registry

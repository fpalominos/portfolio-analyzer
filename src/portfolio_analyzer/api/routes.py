from fastapi import APIRouter, Depends

from portfolio_analyzer.analytics.portfolio_analytics import PortfolioAnalytics
from portfolio_analyzer.api.dependencies import get_valuator
from portfolio_analyzer.domain.portfolio import Portfolio
from portfolio_analyzer.domain.stock import Stock
from portfolio_analyzer.models.portfolio_value import PortfolioValueResponse
from portfolio_analyzer.services.portfolio_valuator import PortfolioValuator

router = APIRouter()


def create_portfolio() -> Portfolio:
    return (
        Portfolio()
        .add_position(Stock("AAPL", 10))
        .add_position(Stock("MSFT", 5))
        .add_position(Stock("NVDA", 3))
    )


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get(
    "/portfolio/value",
    response_model=PortfolioValueResponse,
)
async def portfolio_value(
        valuator: PortfolioValuator = Depends(get_valuator),
):
    portfolio = create_portfolio()

    positions = await valuator.value_positions(portfolio)

    total_value = PortfolioAnalytics.total_value(positions)

    return PortfolioValueResponse(total_value=total_value)

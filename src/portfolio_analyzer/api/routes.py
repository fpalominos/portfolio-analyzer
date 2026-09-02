from fastapi import APIRouter, Depends

from portfolio_analyzer.analytics.portfolio_analytics import PortfolioAnalytics
from portfolio_analyzer.api.dependencies import get_valuator, get_portfolio_repository, get_llm_service
from portfolio_analyzer.domain.portfolio import Portfolio
from portfolio_analyzer.domain.stock import Stock
from portfolio_analyzer.exceptions.portfolio import PortfolioNotFoundError
from portfolio_analyzer.models.portfolio import PortfolioCreateRequest, \
    PortfolioPositionResponse, PortfolioResponse
from portfolio_analyzer.models.portfolio_value import PortfolioValueResponse
from portfolio_analyzer.repositories.portfolio_repository import PortfolioRepository
from portfolio_analyzer.services.llm_service import LLMService
from portfolio_analyzer.services.portfolio_valuator import PortfolioValuator
from portfolio_analyzer.models.llm_service import PortfolioAnalysisRequest, PortfolioAnalysisResponse

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get(
    "/portfolio/value",
    response_model=PortfolioValueResponse,
)
async def portfolio_value(
        valuator: PortfolioValuator = Depends(get_valuator),
        repository: PortfolioRepository = Depends(get_portfolio_repository),
) -> PortfolioValueResponse:
    portfolio = repository.get()

    if portfolio is None:
        raise PortfolioNotFoundError("Portfolio not found")

    positions = await valuator.value_positions(portfolio)

    total_value = PortfolioAnalytics.total_value(positions)

    return PortfolioValueResponse(total_value=total_value)


@router.post("/portfolio", response_model=PortfolioResponse)
def create_portfolio(
        request: PortfolioCreateRequest,
        repository: PortfolioRepository = Depends(get_portfolio_repository),
) -> PortfolioResponse:
    # todo: remove. Just for local development
    # portfolio = (Portfolio()
    #              .add_position(Stock("AAPL", 10))
    #              .add_position(Stock("MSFT", 5))
    #              .add_position(Stock("NVDA", 3)))

    portfolio = Portfolio()

    for position in request.positions:
        portfolio = portfolio.add_position(
            Stock(position.symbol, position.shares)
        )

    repository.save(portfolio=portfolio)

    positions = [PortfolioPositionResponse(
        symbol=position.symbol,
        shares=position.shares)
        for position in portfolio.positions
    ]

    return PortfolioResponse(positions=positions)


@router.post("/portfolio/analyse", response_model=PortfolioAnalysisResponse)
async def analyse(
        request: PortfolioAnalysisRequest,
        llm_service: LLMService = Depends(get_llm_service)
) -> PortfolioAnalysisResponse:
    response = await llm_service.analyse(request.prompt)
    return PortfolioAnalysisResponse(response=response)

# todo: remove. Just for local development
# if __name__ == '__main__':
#     nvidia = PortfolioValueRequest(symbol="NVDA", shares=3)
#     msft = PortfolioValueRequest(symbol="MSFT", shares=5)
#
#     request = PortfolioCreateRequest(positions=[nvidia, msft])
#     r = create_portfolio(request)
#
#     print(f"r: {r}")

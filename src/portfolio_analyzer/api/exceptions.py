from fastapi import Request
from fastapi.responses import JSONResponse

from portfolio_analyzer.exceptions.llm_service import LLMServiceError
from portfolio_analyzer.exceptions.portfolio import PortfolioNotFoundError
from portfolio_analyzer.exceptions.price_service import InvalidSymbolError, PriceServiceError


async def price_service_exception_handler(
        _request: Request,
        exc: PriceServiceError,
) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )


async def invalid_symbol_exception_handler(
        _request: Request,
        exc: InvalidSymbolError,
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


async def portfolio_not_found_exception_handler(
        _request: Request,
        exc: PortfolioNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )


async def llm_service_exception_handler(
        _request: Request,
        exc: LLMServiceError,
) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

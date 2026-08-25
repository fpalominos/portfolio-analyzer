from fastapi import Request
from fastapi.responses import JSONResponse


async def price_service_exception_handler(
        _request: Request,
        exc: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )


async def invalid_symbol_exception_handler(
        _request: Request,
        exc: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )

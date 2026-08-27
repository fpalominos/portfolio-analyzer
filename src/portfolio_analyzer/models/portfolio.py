from pydantic import BaseModel


class PortfolioValueRequest(BaseModel):
    symbol: str
    shares: int

class PortfolioCreateRequest(BaseModel):
    positions: list[PortfolioValueRequest]

class PortfolioPositionResponse(BaseModel):
    symbol: str
    shares: int

class PortfolioResponse(BaseModel):
    positions: list[PortfolioPositionResponse]

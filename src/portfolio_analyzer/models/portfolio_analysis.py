from pydantic import BaseModel


class PortfolioAnalysis(BaseModel):
    summary: str
    diversification: str
    risks: list[str]
    recommendations: list[str]

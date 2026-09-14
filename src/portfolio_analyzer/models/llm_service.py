from pydantic import BaseModel
from portfolio_analyzer.models.portfolio_analysis import PortfolioAnalysis


class PortfolioAnalysisRequest(BaseModel):
    prompt: str

class PortfolioAnalysisResponse(BaseModel):
    analysis: PortfolioAnalysis
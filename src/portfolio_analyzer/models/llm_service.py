from pydantic import BaseModel


class PortfolioAnalysisRequest(BaseModel):
    prompt: str

class PortfolioAnalysisResponse(BaseModel):
    response: str
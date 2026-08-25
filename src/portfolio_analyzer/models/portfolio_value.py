from pydantic import BaseModel


class PortfolioValueResponse(BaseModel):
    total_value: float

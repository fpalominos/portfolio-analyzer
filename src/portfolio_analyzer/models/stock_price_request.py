from pydantic import BaseModel

class StockPriceRequest(BaseModel):
    symbol: str
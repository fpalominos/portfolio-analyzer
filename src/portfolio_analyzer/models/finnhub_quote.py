from pydantic import BaseModel, Field


class FinnhubQuote(BaseModel):
    current_price: float = Field(alias="c")
    high: float = Field(alias="h")
    low: float = Field(alias="l")
    open: float = Field(alias="o")
    previous_close: float = Field(alias="pc")


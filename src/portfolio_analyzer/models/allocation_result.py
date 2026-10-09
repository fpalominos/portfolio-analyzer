from pydantic import BaseModel


class AllocationResult(BaseModel):
    symbol: str
    weight: float

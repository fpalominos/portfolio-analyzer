from openai import pydantic_function_tool

from portfolio_analyzer.models.stock_price_request import StockPriceRequest


def get_stock_price_tool():
    return pydantic_function_tool(StockPriceRequest, name="get_stock_price")

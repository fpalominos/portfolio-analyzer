from portfolio_analyzer.tools.definitions import get_stock_price_tool


def test_get_stock_price_tool_definition():
    tool = get_stock_price_tool()["function"]

    assert tool["name"] == "get_stock_price"
    assert tool["strict"] is True
    assert tool["parameters"]["properties"]["symbol"]["title"] == "Symbol"
    assert tool["parameters"]["properties"]["symbol"]["type"] == "string"
    assert tool["parameters"]["required"] == ["symbol"]
    assert tool["parameters"]["title"] == "StockPriceRequest"
    assert tool["parameters"]["type"] == "object"
    assert tool["parameters"]["additionalProperties"] is False
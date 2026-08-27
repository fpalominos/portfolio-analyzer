from fastapi.testclient import TestClient

from portfolio_analyzer.api.dependencies import get_valuator
from portfolio_analyzer.domain.portfolio import Portfolio
from portfolio_analyzer.domain.stock import Stock
from portfolio_analyzer.domain.valued_position import ValuedPosition
from portfolio_analyzer.exceptions.price_service import PriceServiceError, InvalidSymbolError
from portfolio_analyzer.main import app


class FakeValuator:
    async def value_positions(
            self,
            portfolio: Portfolio,
    ) -> tuple[ValuedPosition, ...]:
        return (
            ValuedPosition(
                Stock("AAPL", 10),
                10.0,
            ),
            ValuedPosition(
                Stock("MSFT", 5),
                20.0,
            ),
        )


client = TestClient(app)


class PriceServiceErrorValuator:
    async def value_positions(
            self,
            portfolio: Portfolio,
    ) -> tuple[ValuedPosition, ...]:
        raise PriceServiceError("Unable to retrieve prices")


class InvalidSymbolErrorValuator:
    async def value_positions(
            self,
            portfolio: Portfolio,
    ) -> tuple[ValuedPosition, ...]:
        raise InvalidSymbolError("Unable to retrieve prices for the provided symbol")


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_portfolio_value():
    app.dependency_overrides[get_valuator] = lambda: FakeValuator()

    try:
        response = client.get("/portfolio/value")

        assert response.status_code == 200
        assert response.json() == {"total_value": 200.0}

    finally:
        app.dependency_overrides.clear()


def test_portfolio_value_returns_expected_response():
    app.dependency_overrides[get_valuator] = lambda: FakeValuator()

    try:
        response = client.get("/portfolio/value")

        assert response.status_code == 200

        body = response.json()

        assert "total_value" in body
        assert isinstance(body["total_value"], float)

    finally:
        app.dependency_overrides.clear()


def test_portfolio_value_when_valuation_fails():
    app.dependency_overrides[get_valuator] = lambda: PriceServiceErrorValuator()

    try:
        response = client.get("/portfolio/value")

        assert response.status_code == 500
        assert response.json() == {"detail": "Unable to retrieve prices"}

    finally:
        app.dependency_overrides.clear()


def test_portfolio_value_when_valuation_fails_with_invalid_symbol():
    app.dependency_overrides[get_valuator] = lambda: InvalidSymbolErrorValuator()

    try:
        response = client.get("/portfolio/value")

        assert response.status_code == 400
        assert response.json() == {"detail": "Unable to retrieve prices for the provided symbol"}

    finally:
        app.dependency_overrides.clear()


def test_create_portfolio_returns_expected_response():
    data = {
        "positions": [
            {
                "symbol": "NVDA",
                "shares": 10
            },
            {
                "symbol": "MSFT",
                "shares": 20
            }
        ]
    }

    response = client.post("/portfolio", json=data)

    assert response.status_code == 200
    assert response.json() == {'positions': [{'symbol': 'NVDA', 'shares': 10}, {'symbol': 'MSFT', 'shares': 20}]}


def test_create_portfolio_when_shares_is_missing_returns_validation_error():
    data = {
        "positions": [
            {
                "symbol": "NVDA",
            }
        ]
    }

    response = client.post("/portfolio", json=data)

    assert response.status_code == 422

    body = response.json()

    assert body["detail"][0]["loc"] == [
        "body", "positions", 0, "shares"
    ]

def test_create_portfolio_when_symbol_is_missing_returns_validation_error():
    data = {
        "positions": [
            {
                "shares": 10,
            }
        ]
    }

    response = client.post("/portfolio", json=data)

    assert response.status_code == 422

    body = response.json()

    assert body["detail"][0]["loc"] == [
        "body", "positions", 0, "symbol"
    ]

def test_create_portfolio_when_shares_is_invalid_returns_validation_error():
    data = {
        "positions": [
            {
                "symbol": "NVDA",
                "shares": "INVALID",
            }
        ]
    }

    response = client.post("/portfolio", json=data)

    assert response.status_code == 422

    body = response.json()

    assert body["detail"][0]["loc"] == [
        "body", "positions", 0, "symbol"
    ]

    assert body["detail"][0]["type"] == "int_parsing"

def test_create_empty_portfolio_returns_empty_positions():
    data = {
        "positions": []
    }

    response = client.post("/portfolio", json=data)

    assert response.status_code == 200
    assert response.json() == {
        "positions": []
    }

def test_create_portfolio_when_positions_is_missing_returns_validation_error():
    data = {}

    response = client.post("/portfolio", json=data)

    assert response.status_code == 422

    body = response.json()

    assert body["detail"][0]["loc"] == [
        "body", "positions"
    ]

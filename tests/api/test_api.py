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

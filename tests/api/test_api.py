from textwrap import dedent

from fastapi.testclient import TestClient

from portfolio_analyzer.api.dependencies import get_valuator, get_portfolio_repository, get_llm_service
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


class FakeValuatorWithKnownPrices:
    async def value_positions(
            self,
            portfolio: Portfolio,
    ) -> tuple[ValuedPosition, ...]:
        return (
            ValuedPosition(
                Stock("NVDA", 10),
                10.0,
            ),
            ValuedPosition(
                Stock("MSFT", 20),
                20.0,
            ),
        )


class FakeLLMService:
    async def analyse(self, prompt: str) -> str:
        return prompt


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


def test_portfolio_value(
        portfolio_repository
):
    app.dependency_overrides[get_valuator] = lambda: FakeValuator()
    app.dependency_overrides[get_portfolio_repository] = lambda: portfolio_repository

    portfolio = Portfolio().add_position(Stock("AAPL", 10))

    portfolio_repository.save(portfolio)

    try:
        response = client.get("/portfolio/value")

        assert response.status_code == 200
        assert response.json() == {"total_value": 200.0}

    finally:
        app.dependency_overrides.clear()


def test_portfolio_value_returns_expected_response(
        portfolio_repository,
        portfolio
):
    app.dependency_overrides[get_valuator] = lambda: FakeValuator()
    app.dependency_overrides[get_portfolio_repository] = lambda: portfolio_repository

    portfolio_repository.save(portfolio)
    try:
        response = client.get("/portfolio/value")

        assert response.status_code == 200

        body = response.json()

        assert "total_value" in body
        assert isinstance(body["total_value"], float)

    finally:
        app.dependency_overrides.clear()


def test_portfolio_value_when_valuation_fails(
        portfolio_repository,
        portfolio,
):
    app.dependency_overrides[get_valuator] = lambda: PriceServiceErrorValuator()
    app.dependency_overrides[get_portfolio_repository] = lambda: portfolio_repository

    portfolio_repository.save(portfolio)

    try:
        response = client.get("/portfolio/value")

        assert response.status_code == 500
        assert response.json() == {"detail": "Unable to retrieve prices"}

    finally:
        app.dependency_overrides.clear()


def test_portfolio_value_when_valuation_fails_with_invalid_symbol(
        portfolio_repository,
        portfolio
):
    app.dependency_overrides[get_valuator] = lambda: InvalidSymbolErrorValuator()
    app.dependency_overrides[get_portfolio_repository] = lambda: portfolio_repository

    portfolio_repository.save(portfolio)

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
        "body", "positions", 0, "shares"
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


def test_portfolio_value_when_portfolio_does_not_exist_returns_not_found(
        portfolio_repository,
        portfolio
):
    app.dependency_overrides[get_portfolio_repository] = lambda: portfolio_repository

    try:
        response = client.get("/portfolio/value")

        assert response.status_code == 404

        body = response.json()

        assert body["detail"] == "Portfolio not found"

    finally:
        app.dependency_overrides.clear()


def test_create_portfolio_then_get_portfolio_value(
        portfolio_repository,
):
    app.dependency_overrides[get_valuator] = lambda: FakeValuatorWithKnownPrices()
    app.dependency_overrides[get_portfolio_repository] = lambda: portfolio_repository
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
    try:
        create_response = client.post("/portfolio", json=data)

        assert create_response.status_code == 200
        assert create_response.json() == {
            "positions": [
                {"symbol": "NVDA", "shares": 10},
                {"symbol": "MSFT", "shares": 20},
            ]
        }

        value_response = client.get("/portfolio/value")

        assert value_response.status_code == 200
        assert value_response.json() == {"total_value": 500.0}


    finally:
        app.dependency_overrides.clear()


def test_portfolio_analyse_returns_expected_response(
        portfolio_repository,
):
    app.dependency_overrides[get_portfolio_repository] = lambda: portfolio_repository
    app.dependency_overrides[get_valuator] = lambda: FakeValuatorWithKnownPrices()
    app.dependency_overrides[get_llm_service] = lambda: FakeLLMService()

    portfolio = (Portfolio()
                 .add_position(Stock(symbol="NVDA", shares=10))
                 .add_position(Stock(symbol="MSFT", shares=20)))

    portfolio_repository.save(portfolio)

    data = {"prompt": "Is my portfolio diversified?"}

    expected_json_response = {f"response": dedent("""\
        Here's the user's portfolio:
        
        NVDA: 10 shares, current price: $10.00, market value: $100.00
        MSFT: 20 shares, current price: $20.00, market value: $400.00
        
        User's question:
        Is my portfolio diversified?
        
        Analyse the portfolio and answer the user's question""")}

    try:

        response = client.post("/portfolio/analyse", json=data)

        assert response.status_code == 200
        assert response.json() == expected_json_response

    finally:
        app.dependency_overrides.clear()


def test_portfolio_analyse_when_prompt_is_missing_returns_validation_error():
    data = {"another_field": "another value"}

    response = client.post("/portfolio/analyse", json=data)

    assert response.status_code == 422

    body = response.json()

    assert body["detail"][0]["loc"] == ['body', 'prompt']

    assert body["detail"][0]["type"] == "missing"


def test_portfolio_analyse_when_prompt_is_invalid_returns_validation_error():
    data = {"prompt": 1234}

    response = client.post("/portfolio/analyse", json=data)

    assert response.status_code == 422

    body = response.json()

    assert body["detail"][0]["loc"] == ['body', 'prompt']

    assert body["detail"][0]["type"] == "string_type"

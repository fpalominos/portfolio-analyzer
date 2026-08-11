import httpx
from pydantic import ValidationError

from portfolio_analyzer.exceptions.price_service import InvalidApiKeyError, InvalidSymbolError
from portfolio_analyzer.exceptions.price_service import PriceServiceError
from portfolio_analyzer.models.finnhub_quote import FinnhubQuote


class PriceService:
    BASE_URL = "https://finnhub.io/api/v1"

    def __init__(
            self,
            client: httpx.AsyncClient,
            api_key: str
    ) -> None:
        self.client = client
        self.api_key = api_key

    async def get_quote(
            self,
            symbol: str) -> FinnhubQuote:
        params = {'symbol': symbol, 'token': self.api_key}
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/quote",
                params=params
            )

            response.raise_for_status()
            data = response.json()
            parsed_quote: FinnhubQuote = self._parse_quote(data)
            if parsed_quote.current_price == 0:
                raise InvalidSymbolError(
                    f"Finnhub does not recognise this symbol: {symbol}"
                )
            return parsed_quote
        except httpx.HTTPStatusError as e:

            if e.response.status_code == 401:
                raise InvalidApiKeyError(
                    "Finnhub API key is invalid."
                ) from e
            raise PriceServiceError(
                f"Finnhub return HTTP {e.response.status_code}"
            ) from e
        except httpx.RequestError as e:
            raise PriceServiceError(
                f"Could not connect to Finnhub."
            ) from e

    async def get_price(
            self,
            symbol: str) -> float:
        quote = await self.get_quote(symbol)
        return quote.current_price

    @staticmethod
    def _parse_quote(
            data: dict) -> FinnhubQuote:

        if "error" in data:
            match data["error"]:
                case "Invalid API key.":
                    raise InvalidApiKeyError()
                case _:
                    raise PriceServiceError(data["error"])

        try:
            return FinnhubQuote.model_validate(data)
        except ValidationError as e:
            raise PriceServiceError(
                "Unexpected response from Finnhub."
            ) from e

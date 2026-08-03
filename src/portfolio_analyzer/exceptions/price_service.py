class PriceServiceError(Exception):
    """Base exception for all price service errors."""

class InvalidApiKeyError(PriceServiceError):
    """The configured API key was rejected."""

class InvalidSymbolError(PriceServiceError):
    """The requested symbol does not exist."""

class PriceUnavailableError(PriceServiceError):
    """A price could not be obtained."""
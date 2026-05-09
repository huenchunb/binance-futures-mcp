class BinanceMCPError(Exception):
    """Base class for all domain exceptions in this project."""
    def __init__(self, message: str, code: str, details: str = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details

class InvalidCredentialsError(BinanceMCPError):
    """Raised when the API Key or Secret are invalid or missing."""
    def __init__(self, message: str = "Invalid API Credentials", details: str = None):
        super().__init__(message, code="INVALID_CREDENTIALS", details=details)

class BinanceAPIError(BinanceMCPError):
    """Raised when Binance API returns an error (e.g., rate limit, server error)."""
    def __init__(self, message: str, details: str = None):
        super().__init__(message, code="BINANCE_API_ERROR", details=details)

class ServiceUnavailableError(BinanceMCPError):
    """Raised when the Circuit Breaker is open or the service is completely unreachable."""
    def __init__(self, message: str = "Service temporarily unavailable. Circuit Breaker is open.", details: str = None):
        super().__init__(message, code="SERVICE_UNAVAILABLE", details=details)

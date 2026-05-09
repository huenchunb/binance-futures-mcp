import time
from typing import Callable, Any
from functools import wraps
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from binance_futures_mcp.errors import BinanceAPIError, ServiceUnavailableError

# Retry configuration
# Retries 3 times (4 attempts total), waiting 2^x * 1 seconds between each retry
with_retry = retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(BinanceAPIError),
    reraise=True
)

class CircuitBreaker:
    """A simple Circuit Breaker implementation."""
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = 0
        self.state = "CLOSED" # CLOSED, OPEN, HALF_OPEN

    def call(self, func: Callable, *args, **kwargs) -> Any:
        self._check_state()

        if self.state == "OPEN":
            raise ServiceUnavailableError("Circuit Breaker is OPEN. Not calling Binance API.")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except BinanceAPIError as e:
            self._on_failure()
            raise e
        except Exception as e:
            # For non-domain exceptions, we might also want to fail the circuit, 
            # but let's stick to API errors for Binance limits/timeouts
            self._on_failure()
            raise e

    def _check_state(self):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"

    def _on_success(self):
        self.failures = 0
        self.state = "CLOSED"

    def _on_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"

# Global circuit breaker instance
circuit_breaker = CircuitBreaker()

def with_circuit_breaker(func):
    """Decorator to wrap a function with the global circuit breaker."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        return circuit_breaker.call(func, *args, **kwargs)
    return wrapper

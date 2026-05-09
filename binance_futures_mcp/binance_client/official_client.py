from typing import Dict, Any
from binance.um_futures import UMFutures
from binance.error import ClientError

from binance_futures_mcp.binance_client.base import BaseBinanceClient
from binance_futures_mcp.errors import InvalidCredentialsError, BinanceAPIError
from binance_futures_mcp.resilience import with_retry, with_circuit_breaker

class OfficialBinanceClient(BaseBinanceClient):
    """Implementation using the official binance-futures-connector."""
    
    def __init__(self, api_key: str, api_secret: str):
        self.client = UMFutures(key=api_key, secret=api_secret)

    @with_circuit_breaker
    @with_retry
    def get_usdt_balance(self) -> Dict[str, Any]:
        try:
            # v3 of the API: balance endpoint
            response = self.client.balance()
            
            # response is a list of asset balances
            # Find USDT
            usdt_info = next((item for item in response if item.get('asset') == 'USDT'), None)
            
            if not usdt_info:
                # If USDT is not found, default to zero
                return {
                    "balance": "0.0",
                    "available_balance": "0.0"
                }
                
            return {
                "balance": str(usdt_info.get("balance", "0.0")),
                "available_balance": str(usdt_info.get("withdrawAvailable", "0.0"))
            }

        except ClientError as e:
            # ClientError from official library has status_code, error_code, error_message
            status_code = getattr(e, "status_code", 500)
            if status_code == 401 or getattr(e, "error_code", 0) == -2015:
                raise InvalidCredentialsError(details=getattr(e, "error_message", str(e)))
            
            raise BinanceAPIError(message=f"Binance Official API Error: {getattr(e, 'error_message', str(e))}", details=str(e))
        except Exception as e:
            raise BinanceAPIError(message=f"Unexpected error: {str(e)}")

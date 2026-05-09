from typing import Dict, Any
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

from binance_futures_mcp.binance_client.base import BaseBinanceClient
from binance_futures_mcp.errors import InvalidCredentialsError, BinanceAPIError
from binance_futures_mcp.resilience import with_retry, with_circuit_breaker

class CommunityBinanceClient(BaseBinanceClient):
    """Implementation using the popular python-binance community library."""
    
    def __init__(self, api_key: str, api_secret: str):
        self.client = Client(api_key, api_secret)

    @with_circuit_breaker
    @with_retry
    def get_usdt_balance(self) -> Dict[str, Any]:
        try:
            # Futures balance endpoint
            response = self.client.futures_account_balance()
            
            # response is a list of asset balances
            # Find USDT
            usdt_info = next((item for item in response if item.get('asset') == 'USDT'), None)
            
            if not usdt_info:
                return {
                    "balance": "0.0",
                    "available_balance": "0.0"
                }
                
            return {
                "balance": str(usdt_info.get("balance", "0.0")),
                "available_balance": str(usdt_info.get("withdrawAvailable", "0.0"))
            }

        except BinanceAPIException as e:
            if e.status_code == 401 or e.code == -2015:
                raise InvalidCredentialsError(details=e.message)
            raise BinanceAPIError(message=f"Binance Community API Error: {e.message}", details=str(e))
        except BinanceRequestException as e:
            raise BinanceAPIError(message=f"Binance Community Request Error: {str(e)}")
        except Exception as e:
            raise BinanceAPIError(message=f"Unexpected error: {str(e)}")

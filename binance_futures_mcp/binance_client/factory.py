from typing import Dict, Any, List

from binance_futures_mcp.binance_client.base import BaseBinanceClient
from binance_futures_mcp.binance_client.official_client import OfficialBinanceClient
from binance_futures_mcp.binance_client.community_client import CommunityBinanceClient
from binance_futures_mcp.errors import BinanceAPIError, InvalidCredentialsError

class ResilientFallbackClient(BaseBinanceClient):
    """
    A client that tries the official client first.
    If it fails with a generic API/connection error, it falls back to the community client.
    """
    def __init__(self, api_key: str, api_secret: str):
        self.official_client = OfficialBinanceClient(api_key, api_secret)
        self.community_client = CommunityBinanceClient(api_key, api_secret)

    def get_usdt_balance(self) -> Dict[str, Any]:
        try:
            return self.official_client.get_usdt_balance()
        except InvalidCredentialsError as e:
            # Do not fallback on auth errors, they will fail on the community client anyway
            raise e
        except BinanceAPIError as e:
            # Fallback to community client
            print(f"Official client failed: {e.message}. Falling back to community client...")
            return self.community_client.get_usdt_balance()

    def get_open_positions(self) -> List[Dict[str, Any]]:
        try:
            return self.official_client.get_open_positions()
        except InvalidCredentialsError as e:
            # Do not fallback on auth errors, they will fail on the community client anyway
            raise e
        except BinanceAPIError as e:
            # Fallback to community client
            print(f"Official client failed: {e.message}. Falling back to community client...")
            return self.community_client.get_open_positions()

class BinanceClientFactory:
    """Factory to instantiate the Binance Client."""
    
    @staticmethod
    def create_client(api_key: str, api_secret: str) -> BaseBinanceClient:
        """
        Returns a resilient client that uses the official connector by default
        and falls back to the community library on connection errors.
        """
        return ResilientFallbackClient(api_key, api_secret)


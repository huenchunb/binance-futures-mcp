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

    def get_open_orders(self) -> List[Dict[str, Any]]:
        try:
            return self.official_client.get_open_orders()
        except InvalidCredentialsError as e:
            raise e
        except BinanceAPIError as e:
            print(f"Official client failed: {e.message}. Falling back to community client...")
            return self.community_client.get_open_orders()

    def get_all_orders(self, symbol: str) -> List[Dict[str, Any]]:
        try:
            return self.official_client.get_all_orders(symbol)
        except InvalidCredentialsError as e:
            raise e
        except BinanceAPIError as e:
            print(f"Official client failed: {e.message}. Falling back to community client...")
            return self.community_client.get_all_orders(symbol)

    def create_order(self, order_params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return self.official_client.create_order(order_params)
        except InvalidCredentialsError as e:
            raise e
        except BinanceAPIError as e:
            print(f"Official client failed: {e.message}. Falling back to community client...")
            return self.community_client.create_order(order_params)

    def create_batch_orders(self, orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        try:
            return self.official_client.create_batch_orders(orders)
        except InvalidCredentialsError as e:
            raise e
        except BinanceAPIError as e:
            print(f"Official client failed: {e.message}. Falling back to community client...")
            return self.community_client.create_batch_orders(orders)

    def modify_order(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return self.official_client.modify_order(params)
        except InvalidCredentialsError as e:
            raise e
        except BinanceAPIError as e:
            print(f"Official client failed: {e.message}. Falling back to community client...")
            return self.community_client.modify_order(params)

    def modify_batch_orders(self, orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        try:
            return self.official_client.modify_batch_orders(orders)
        except InvalidCredentialsError as e:
            raise e
        except BinanceAPIError as e:
            print(f"Official client failed: {e.message}. Falling back to community client...")
            return self.community_client.modify_batch_orders(orders)

    def get_order_modify_history(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            return self.official_client.get_order_modify_history(params)
        except InvalidCredentialsError as e:
            raise e
        except BinanceAPIError as e:
            print(f"Official client failed: {e.message}. Falling back to community client...")
            return self.community_client.get_order_modify_history(params)

    def cancel_order(self, symbol: str, order_id: int = None, orig_client_order_id: str = None) -> Dict[str, Any]:
        try:
            return self.official_client.cancel_order(symbol, order_id, orig_client_order_id)
        except InvalidCredentialsError as e:
            raise e
        except BinanceAPIError as e:
            print(f"Official client failed: {e.message}. Falling back to community client...")
            return self.community_client.cancel_order(symbol, order_id, orig_client_order_id)

    def cancel_batch_orders(self, symbol: str, order_id_list: List[int]) -> List[Dict[str, Any]]:
        try:
            return self.official_client.cancel_batch_orders(symbol, order_id_list)
        except InvalidCredentialsError as e:
            raise e
        except BinanceAPIError as e:
            print(f"Official client failed: {e.message}. Falling back to community client...")
            return self.community_client.cancel_batch_orders(symbol, order_id_list)

    def cancel_all_open_orders(self, symbol: str) -> Dict[str, Any]:
        try:
            return self.official_client.cancel_all_open_orders(symbol)
        except InvalidCredentialsError as e:
            raise e
        except BinanceAPIError as e:
            print(f"Official client failed: {e.message}. Falling back to community client...")
            return self.community_client.cancel_all_open_orders(symbol)

class BinanceClientFactory:
    """Factory to instantiate the Binance Client."""
    
    @staticmethod
    def create_client(api_key: str, api_secret: str) -> BaseBinanceClient:
        """
        Returns a resilient client that uses the official connector by default
        and falls back to the community library on connection errors.
        """
        return ResilientFallbackClient(api_key, api_secret)


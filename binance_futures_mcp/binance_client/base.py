from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseBinanceClient(ABC):
    @abstractmethod
    def get_usdt_balance(self) -> Dict[str, Any]:
        """
        Retrieves the USDT balance from Binance Futures.
        Must return a dictionary with at least 'balance' and 'available_balance' as strings.
        Raises InvalidCredentialsError or BinanceAPIError on failures.
        """
        pass

    @abstractmethod
    def get_open_positions(self) -> List[Dict[str, Any]]:
        """
        Retrieves all open positions from Binance Futures.
        Must return a list of dictionaries, each containing position details.
        Only positions with positionAmt != 0 should be returned.
        Raises InvalidCredentialsError or BinanceAPIError on failures.
        """
        pass

    @abstractmethod
    def get_open_orders(self) -> List[Dict[str, Any]]:
        """
        Retrieves all open orders across all symbols from Binance Futures.
        Must return a list of dictionaries, each containing order details.
        Raises InvalidCredentialsError or BinanceAPIError on failures.
        """
        pass

    @abstractmethod
    def get_all_orders(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Retrieves all orders (open, filled, canceled) for a specific symbol from Binance Futures.
        Must return a list of dictionaries, each containing order details.
        Raises InvalidCredentialsError or BinanceAPIError on failures.
        """
        pass

    @abstractmethod
    def create_order(self, order_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new order on Binance Futures.
        order_params must include: symbol, side, type, positionSide, and other type-specific params.
        Returns a dictionary with the created order details.
        """
        pass

    @abstractmethod
    def create_batch_orders(self, orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Creates multiple orders (up to 5) on Binance Futures in a single request.
        Returns a list of results, each being either order details or error info.
        """
        pass

    @abstractmethod
    def modify_order(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Modifies an existing LIMIT order on Binance Futures.
        params must include: symbol, side, quantity, price, and orderId or origClientOrderId.
        Returns a dictionary with the modified order details.
        """
        pass

    @abstractmethod
    def modify_batch_orders(self, orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Modifies multiple LIMIT orders (up to 5) on Binance Futures in a single request.
        Returns a list of results, each being either order details or error info.
        """
        pass

    @abstractmethod
    def get_order_modify_history(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Retrieves the modification history for orders on Binance Futures.
        params must include: symbol. Optionally: orderId, origClientOrderId, startTime, endTime, limit.
        Returns a list of amendment records.
        """
        pass

    @abstractmethod
    def cancel_order(self, symbol: str, order_id: int = None, orig_client_order_id: str = None) -> Dict[str, Any]:
        """
        Cancels an active order on Binance Futures.
        Requires symbol and at least one of orderId or origClientOrderId.
        Returns a dictionary with the canceled order details.
        """
        pass

    @abstractmethod
    def cancel_batch_orders(self, symbol: str, order_id_list: List[int]) -> List[Dict[str, Any]]:
        """
        Cancels multiple orders (up to 10) on Binance Futures in a single request.
        Returns a list of results for each cancellation.
        """
        pass

    @abstractmethod
    def cancel_all_open_orders(self, symbol: str) -> Dict[str, Any]:
        """
        Cancels all open orders for a specific symbol on Binance Futures.
        Returns a dictionary with the operation result (code and message).
        """
        pass



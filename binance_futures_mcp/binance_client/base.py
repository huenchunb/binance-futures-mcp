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


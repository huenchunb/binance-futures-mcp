from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseBinanceClient(ABC):
    @abstractmethod
    def get_usdt_balance(self) -> Dict[str, Any]:
        """
        Retrieves the USDT balance from Binance Futures.
        Must return a dictionary with at least 'balance' and 'available_balance' as strings.
        Raises InvalidCredentialsError or BinanceAPIError on failures.
        """
        pass

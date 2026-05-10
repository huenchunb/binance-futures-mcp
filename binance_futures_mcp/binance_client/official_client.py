from typing import Dict, Any, List
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

    @with_circuit_breaker
    @with_retry
    def get_open_positions(self) -> List[Dict[str, Any]]:
        try:
            # v3 of the API: positionRisk endpoint
            response = self.client.get_position_risk()
            
            # Filter only active positions (positionAmt != 0)
            active_positions = [
                {
                    "symbol": pos.get("symbol", ""),
                    "position_side": pos.get("positionSide", "BOTH"),
                    "position_amount": str(pos.get("positionAmt", "0")),
                    "entry_price": str(pos.get("entryPrice", "0.0")),
                    "break_even_price": str(pos.get("breakEvenPrice", "0.0")),
                    "mark_price": str(pos.get("markPrice", "0.0")),
                    "liquidation_price": str(pos.get("liquidationPrice", "0.0")),
                    "leverage": str(pos.get("leverage", "1")),
                    "unrealized_profit": str(pos.get("unRealizedProfit", "0.0")),
                    "margin_type": pos.get("marginType", "cross"),
                    "initial_margin": str(pos.get("initialMargin", "0.0")),
                    "maint_margin": str(pos.get("maintMargin", "0.0")),
                    "notional": str(pos.get("notional", "0.0")),
                    "isolated_margin": str(pos.get("isolatedMargin", "0.0")),
                    "update_time": int(pos.get("updateTime", 0)),
                }
                for pos in response
                if float(pos.get("positionAmt", 0)) != 0
            ]
            
            return active_positions

        except ClientError as e:
            status_code = getattr(e, "status_code", 500)
            if status_code == 401 or getattr(e, "error_code", 0) == -2015:
                raise InvalidCredentialsError(details=getattr(e, "error_message", str(e)))
            
            raise BinanceAPIError(message=f"Binance Official API Error: {getattr(e, 'error_message', str(e))}", details=str(e))
        except Exception as e:
            raise BinanceAPIError(message=f"Unexpected error: {str(e)}")


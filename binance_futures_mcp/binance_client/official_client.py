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

    def _map_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Maps a raw Binance order response to the internal model format."""
        return {
            "order_id": int(order.get("orderId", 0)),
            "symbol": order.get("symbol", ""),
            "type": order.get("type", ""),
            "side": order.get("side", ""),
            "position_side": order.get("positionSide", "BOTH"),
            "status": order.get("status", ""),
            "price": str(order.get("price", "0")),
            "stop_price": str(order.get("stopPrice", "0")),
            "orig_qty": str(order.get("origQty", "0")),
            "executed_qty": str(order.get("executedQty", "0")),
            "avg_price": str(order.get("avgPrice", "0")),
            "reduce_only": bool(order.get("reduceOnly", False)),
            "close_position": bool(order.get("closePosition", False)),
            "time_in_force": order.get("timeInForce", "GTC"),
            "working_type": order.get("workingType", "CONTRACT_PRICE"),
            "time": int(order.get("time", 0)),
            "update_time": int(order.get("updateTime", 0)),
        }

    @with_circuit_breaker
    @with_retry
    def get_open_orders(self) -> List[Dict[str, Any]]:
        try:
            response = self.client.get_open_orders()
            return [self._map_order(order) for order in response]

        except ClientError as e:
            status_code = getattr(e, "status_code", 500)
            if status_code == 401 or getattr(e, "error_code", 0) == -2015:
                raise InvalidCredentialsError(details=getattr(e, "error_message", str(e)))
            
            raise BinanceAPIError(message=f"Binance Official API Error: {getattr(e, 'error_message', str(e))}", details=str(e))
        except Exception as e:
            raise BinanceAPIError(message=f"Unexpected error: {str(e)}")

    @with_circuit_breaker
    @with_retry
    def get_all_orders(self, symbol: str) -> List[Dict[str, Any]]:
        try:
            response = self.client.get_all_orders(symbol=symbol)
            return [self._map_order(order) for order in response]

        except ClientError as e:
            status_code = getattr(e, "status_code", 500)
            if status_code == 401 or getattr(e, "error_code", 0) == -2015:
                raise InvalidCredentialsError(details=getattr(e, "error_message", str(e)))
            
            raise BinanceAPIError(message=f"Binance Official API Error: {getattr(e, 'error_message', str(e))}", details=str(e))
        except Exception as e:
            raise BinanceAPIError(message=f"Unexpected error: {str(e)}")

    def _map_order_response(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Maps a raw Binance order creation/modification/cancellation response to the internal model format."""
        return {
            "order_id": int(order.get("orderId", 0)),
            "client_order_id": order.get("clientOrderId", ""),
            "symbol": order.get("symbol", ""),
            "status": order.get("status", ""),
            "type": order.get("type", ""),
            "side": order.get("side", ""),
            "position_side": order.get("positionSide", "BOTH"),
            "price": str(order.get("price", "0")),
            "orig_qty": str(order.get("origQty", "0")),
            "executed_qty": str(order.get("executedQty", "0")),
            "avg_price": str(order.get("avgPrice", "0")),
            "stop_price": str(order.get("stopPrice", "0")),
            "time_in_force": order.get("timeInForce", "GTC"),
            "working_type": order.get("workingType", "CONTRACT_PRICE"),
            "reduce_only": bool(order.get("reduceOnly", False)),
            "close_position": bool(order.get("closePosition", False)),
            "update_time": int(order.get("updateTime", 0)),
        }

    @with_circuit_breaker
    @with_retry
    def create_order(self, order_params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = self.client.new_order(**order_params)
            return self._map_order_response(response)

        except ClientError as e:
            status_code = getattr(e, "status_code", 500)
            if status_code == 401 or getattr(e, "error_code", 0) == -2015:
                raise InvalidCredentialsError(details=getattr(e, "error_message", str(e)))
            raise BinanceAPIError(message=f"Binance Official API Error: {getattr(e, 'error_message', str(e))}", details=str(e))
        except Exception as e:
            raise BinanceAPIError(message=f"Unexpected error: {str(e)}")

    @with_circuit_breaker
    @with_retry
    def create_batch_orders(self, orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        try:
            import json
            response = self.client.new_batch_order(batchOrders=json.dumps(orders))
            results = []
            for item in response:
                if "orderId" in item:
                    results.append({"success": True, "order": self._map_order_response(item)})
                else:
                    results.append({
                        "success": False,
                        "error_code": str(item.get("code", "UNKNOWN")),
                        "error_message": item.get("msg", "Unknown error")
                    })
            return results

        except ClientError as e:
            status_code = getattr(e, "status_code", 500)
            if status_code == 401 or getattr(e, "error_code", 0) == -2015:
                raise InvalidCredentialsError(details=getattr(e, "error_message", str(e)))
            raise BinanceAPIError(message=f"Binance Official API Error: {getattr(e, 'error_message', str(e))}", details=str(e))
        except Exception as e:
            raise BinanceAPIError(message=f"Unexpected error: {str(e)}")

    @with_circuit_breaker
    @with_retry
    def modify_order(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = self.client.modify_order(**params)
            return self._map_order_response(response)

        except ClientError as e:
            status_code = getattr(e, "status_code", 500)
            if status_code == 401 or getattr(e, "error_code", 0) == -2015:
                raise InvalidCredentialsError(details=getattr(e, "error_message", str(e)))
            raise BinanceAPIError(message=f"Binance Official API Error: {getattr(e, 'error_message', str(e))}", details=str(e))
        except Exception as e:
            raise BinanceAPIError(message=f"Unexpected error: {str(e)}")

    @with_circuit_breaker
    @with_retry
    def modify_batch_orders(self, orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        try:
            import json
            response = self.client.modify_batch_order(batchOrders=json.dumps(orders))
            results = []
            for item in response:
                if "orderId" in item:
                    results.append({"success": True, "order": self._map_order_response(item)})
                else:
                    results.append({
                        "success": False,
                        "error_code": str(item.get("code", "UNKNOWN")),
                        "error_message": item.get("msg", "Unknown error")
                    })
            return results

        except ClientError as e:
            status_code = getattr(e, "status_code", 500)
            if status_code == 401 or getattr(e, "error_code", 0) == -2015:
                raise InvalidCredentialsError(details=getattr(e, "error_message", str(e)))
            raise BinanceAPIError(message=f"Binance Official API Error: {getattr(e, 'error_message', str(e))}", details=str(e))
        except Exception as e:
            raise BinanceAPIError(message=f"Unexpected error: {str(e)}")

    @with_circuit_breaker
    @with_retry
    def get_order_modify_history(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            response = self.client.get_order_modify_history(**params)
            results = []
            for item in response:
                amendment = item.get("amendment", {})
                price_info = amendment.get("price", {})
                qty_info = amendment.get("origQty", {})
                results.append({
                    "amendment_id": int(item.get("amendmentId", 0)),
                    "symbol": item.get("symbol", ""),
                    "order_id": int(item.get("orderId", 0)),
                    "client_order_id": item.get("clientOrderId", ""),
                    "time": int(item.get("time", 0)),
                    "price_change": {
                        "before": str(price_info.get("before", "0")),
                        "after": str(price_info.get("after", "0")),
                    },
                    "qty_change": {
                        "before": str(qty_info.get("before", "0")),
                        "after": str(qty_info.get("after", "0")),
                    },
                    "amendment_count": int(amendment.get("count", 0)),
                })
            return results

        except ClientError as e:
            status_code = getattr(e, "status_code", 500)
            if status_code == 401 or getattr(e, "error_code", 0) == -2015:
                raise InvalidCredentialsError(details=getattr(e, "error_message", str(e)))
            raise BinanceAPIError(message=f"Binance Official API Error: {getattr(e, 'error_message', str(e))}", details=str(e))
        except Exception as e:
            raise BinanceAPIError(message=f"Unexpected error: {str(e)}")

    @with_circuit_breaker
    @with_retry
    def cancel_order(self, symbol: str, order_id: int = None, orig_client_order_id: str = None) -> Dict[str, Any]:
        try:
            params = {"symbol": symbol}
            if order_id:
                params["orderId"] = order_id
            if orig_client_order_id:
                params["origClientOrderId"] = orig_client_order_id
            response = self.client.cancel_order(**params)
            return self._map_order_response(response)

        except ClientError as e:
            status_code = getattr(e, "status_code", 500)
            if status_code == 401 or getattr(e, "error_code", 0) == -2015:
                raise InvalidCredentialsError(details=getattr(e, "error_message", str(e)))
            raise BinanceAPIError(message=f"Binance Official API Error: {getattr(e, 'error_message', str(e))}", details=str(e))
        except Exception as e:
            raise BinanceAPIError(message=f"Unexpected error: {str(e)}")

    @with_circuit_breaker
    @with_retry
    def cancel_batch_orders(self, symbol: str, order_id_list: List[int]) -> List[Dict[str, Any]]:
        try:
            response = self.client.cancel_batch_order(symbol=symbol, orderIdList=order_id_list)
            results = []
            for item in response:
                if "orderId" in item and "code" not in item:
                    results.append({"success": True, "order": self._map_order_response(item)})
                else:
                    results.append({
                        "success": False,
                        "error_code": str(item.get("code", "UNKNOWN")),
                        "error_message": item.get("msg", "Unknown error")
                    })
            return results

        except ClientError as e:
            status_code = getattr(e, "status_code", 500)
            if status_code == 401 or getattr(e, "error_code", 0) == -2015:
                raise InvalidCredentialsError(details=getattr(e, "error_message", str(e)))
            raise BinanceAPIError(message=f"Binance Official API Error: {getattr(e, 'error_message', str(e))}", details=str(e))
        except Exception as e:
            raise BinanceAPIError(message=f"Unexpected error: {str(e)}")

    @with_circuit_breaker
    @with_retry
    def cancel_all_open_orders(self, symbol: str) -> Dict[str, Any]:
        try:
            response = self.client.cancel_open_orders(symbol=symbol)
            return {
                "code": int(response.get("code", 200)),
                "message": response.get("msg", "success"),
            }

        except ClientError as e:
            status_code = getattr(e, "status_code", 500)
            if status_code == 401 or getattr(e, "error_code", 0) == -2015:
                raise InvalidCredentialsError(details=getattr(e, "error_message", str(e)))
            raise BinanceAPIError(message=f"Binance Official API Error: {getattr(e, 'error_message', str(e))}", details=str(e))
        except Exception as e:
            raise BinanceAPIError(message=f"Unexpected error: {str(e)}")

    def _map_trade(self, trade: Dict[str, Any]) -> Dict[str, Any]:
        """Maps a raw Binance trade response to the internal model format."""
        return {
            "id": int(trade.get("id", 0)),
            "symbol": trade.get("symbol", ""),
            "order_id": int(trade.get("orderId", 0)),
            "side": trade.get("side", ""),
            "price": str(trade.get("price", "0")),
            "qty": str(trade.get("qty", "0")),
            "realized_pnl": str(trade.get("realizedPnl", "0")),
            "quote_qty": str(trade.get("quoteQty", "0")),
            "commission": str(trade.get("commission", "0")),
            "commission_asset": trade.get("commissionAsset", "USDT"),
            "time": int(trade.get("time", 0)),
            "buyer": bool(trade.get("buyer", False)),
            "maker": bool(trade.get("maker", False)),
            "position_side": trade.get("positionSide", "BOTH"),
        }

    @with_circuit_breaker
    @with_retry
    def query_order(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = self.client.query_order(**params)
            return self._map_order(response)

        except ClientError as e:
            status_code = getattr(e, "status_code", 500)
            if status_code == 401 or getattr(e, "error_code", 0) == -2015:
                raise InvalidCredentialsError(details=getattr(e, "error_message", str(e)))
            raise BinanceAPIError(message=f"Binance Official API Error: {getattr(e, 'error_message', str(e))}", details=str(e))
        except Exception as e:
            raise BinanceAPIError(message=f"Unexpected error: {str(e)}")

    @with_circuit_breaker
    @with_retry
    def query_all_orders(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            response = self.client.get_all_orders(**params)
            return [self._map_order(order) for order in response]

        except ClientError as e:
            status_code = getattr(e, "status_code", 500)
            if status_code == 401 or getattr(e, "error_code", 0) == -2015:
                raise InvalidCredentialsError(details=getattr(e, "error_message", str(e)))
            raise BinanceAPIError(message=f"Binance Official API Error: {getattr(e, 'error_message', str(e))}", details=str(e))
        except Exception as e:
            raise BinanceAPIError(message=f"Unexpected error: {str(e)}")

    @with_circuit_breaker
    @with_retry
    def query_all_open_orders(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            response = self.client.get_open_orders(**params)
            return [self._map_order(order) for order in response]

        except ClientError as e:
            status_code = getattr(e, "status_code", 500)
            if status_code == 401 or getattr(e, "error_code", 0) == -2015:
                raise InvalidCredentialsError(details=getattr(e, "error_message", str(e)))
            raise BinanceAPIError(message=f"Binance Official API Error: {getattr(e, 'error_message', str(e))}", details=str(e))
        except Exception as e:
            raise BinanceAPIError(message=f"Unexpected error: {str(e)}")

    @with_circuit_breaker
    @with_retry
    def query_current_open_order(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = self.client.get_open_orders(**params)
            if isinstance(response, list):
                if len(response) > 0:
                    return self._map_order(response[0])
                return {}
            return self._map_order(response)

        except ClientError as e:
            status_code = getattr(e, "status_code", 500)
            if status_code == 401 or getattr(e, "error_code", 0) == -2015:
                raise InvalidCredentialsError(details=getattr(e, "error_message", str(e)))
            raise BinanceAPIError(message=f"Binance Official API Error: {getattr(e, 'error_message', str(e))}", details=str(e))
        except Exception as e:
            raise BinanceAPIError(message=f"Unexpected error: {str(e)}")

    @with_circuit_breaker
    @with_retry
    def query_force_orders(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            response = self.client.force_orders(**params)
            return [self._map_order(order) for order in response]

        except ClientError as e:
            status_code = getattr(e, "status_code", 500)
            if status_code == 401 or getattr(e, "error_code", 0) == -2015:
                raise InvalidCredentialsError(details=getattr(e, "error_message", str(e)))
            raise BinanceAPIError(message=f"Binance Official API Error: {getattr(e, 'error_message', str(e))}", details=str(e))
        except Exception as e:
            raise BinanceAPIError(message=f"Unexpected error: {str(e)}")

    @with_circuit_breaker
    @with_retry
    def query_trade_list(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            response = self.client.get_account_trades(**params)
            return [self._map_trade(trade) for trade in response]

        except ClientError as e:
            status_code = getattr(e, "status_code", 500)
            if status_code == 401 or getattr(e, "error_code", 0) == -2015:
                raise InvalidCredentialsError(details=getattr(e, "error_message", str(e)))
            raise BinanceAPIError(message=f"Binance Official API Error: {getattr(e, 'error_message', str(e))}", details=str(e))
        except Exception as e:
            raise BinanceAPIError(message=f"Unexpected error: {str(e)}")

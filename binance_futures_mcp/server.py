import os
import json
from typing import Optional
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from binance_futures_mcp.binance_client.factory import BinanceClientFactory
from binance_futures_mcp.errors import BinanceMCPError
from binance_futures_mcp.models import (
    USDTBalance, ErrorResponse, FuturesPosition, OpenPositionsResponse,
    FuturesOrder, OrdersResponse,
    NewOrderResponse, BatchOrderResult, BatchOrderResponse,
    OrderAmendmentDetail, OrderAmendment, OrderAmendmentResponse,
    CancelOrderResponse, CancelAllOrdersResponse,
    TradeRecord, TradeListResponse, ForceOrdersResponse,
)

# Cargar variables de entorno (para desarrollo/pruebas locales)
load_dotenv()

# Inicializar servidor FastMCP
mcp = FastMCP("BinanceFuturesMCP")

@mcp.tool()
def get_usdt_futures_balance() -> str:
    """
    Obtiene el saldo total y disponible en USDT de la cuenta de Binance Futures del usuario.
    Devuelve un objeto JSON con la información del saldo, o un JSON de error si falla.
    """
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        error = ErrorResponse(
            error=True,
            code="MISSING_CREDENTIALS",
            message="Las credenciales de Binance no están configuradas en las variables de entorno."
        )
        return error.model_dump_json()

    try:
        # Usamos el Factory para obtener el cliente resiliente (con Fallback)
        client = BinanceClientFactory.create_client(api_key, api_secret)
        balance_data = client.get_usdt_balance()
        
        # Formatear la respuesta exitosa
        success_response = USDTBalance(**balance_data)
        return success_response.model_dump_json()
        
    except BinanceMCPError as e:
        # Formatear errores de dominio esperados (Credenciales, Circuit Breaker, API Error)
        error_response = ErrorResponse(
            error=True,
            code=e.code,
            message=e.message,
            details=e.details
        )
        return error_response.model_dump_json()
    except Exception as e:
        # Formatear cualquier otro error inesperado
        error_response = ErrorResponse(
            error=True,
            code="INTERNAL_SERVER_ERROR",
            message="Ocurrió un error inesperado al procesar la solicitud.",
            details=str(e)
        )
        return error_response.model_dump_json()

@mcp.tool()
def get_open_positions() -> str:
    """
    Obtiene todas las posiciones abiertas en la cuenta de Binance Futures del usuario.
    Devuelve un JSON con la lista completa de posiciones incluyendo: símbolo, dirección,
    tamaño, precio de entrada, apalancamiento, precio de liquidación, PnL no realizado,
    tipo de margen, margen inicial, margen de mantenimiento, valor nocional y más.
    Solo se devuelven posiciones con cantidad != 0 (realmente abiertas).
    """
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        error = ErrorResponse(
            error=True,
            code="MISSING_CREDENTIALS",
            message="Las credenciales de Binance no están configuradas en las variables de entorno."
        )
        return error.model_dump_json()

    try:
        # Usamos el Factory para obtener el cliente resiliente (con Fallback)
        client = BinanceClientFactory.create_client(api_key, api_secret)
        positions_data = client.get_open_positions()
        
        # Convertir cada posición a modelo Pydantic
        positions = [FuturesPosition(**pos) for pos in positions_data]
        
        # Formatear la respuesta exitosa
        success_response = OpenPositionsResponse(
            count=len(positions),
            positions=positions
        )
        return success_response.model_dump_json()
        
    except BinanceMCPError as e:
        # Formatear errores de dominio esperados (Credenciales, Circuit Breaker, API Error)
        error_response = ErrorResponse(
            error=True,
            code=e.code,
            message=e.message,
            details=e.details
        )
        return error_response.model_dump_json()
    except Exception as e:
        # Formatear cualquier otro error inesperado
        error_response = ErrorResponse(
            error=True,
            code="INTERNAL_SERVER_ERROR",
            message="Ocurrió un error inesperado al procesar la solicitud.",
            details=str(e)
        )
        return error_response.model_dump_json()

@mcp.tool()
def get_orders(symbol: Optional[str] = None) -> str:
    """
    Obtiene las órdenes de la cuenta de Binance Futures del usuario.
    
    Comportamiento:
    - Sin parámetro 'symbol': devuelve todas las órdenes abiertas/pendientes (Stop Loss,
      Take Profit, Limit, etc.) de TODOS los pares. No incluye órdenes canceladas o ejecutadas.
    - Con parámetro 'symbol' (ej. 'BTCUSDT'): devuelve el historial completo de órdenes
      para ese par específico, incluyendo órdenes abiertas, canceladas y ejecutadas.
    
    IMPORTANTE: No confundir con posiciones abiertas (get_open_positions).
    Las órdenes son intenciones de ejecución (SL, TP, Limit) mientras que las
    posiciones son trades activos en el mercado.
    """
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        error = ErrorResponse(
            error=True,
            code="MISSING_CREDENTIALS",
            message="Las credenciales de Binance no están configuradas en las variables de entorno."
        )
        return error.model_dump_json()

    try:
        client = BinanceClientFactory.create_client(api_key, api_secret)
        
        if symbol:
            # Historial completo de órdenes para un símbolo específico
            orders_data = client.get_all_orders(symbol)
            query_type = "all_orders"
        else:
            # Órdenes abiertas/pendientes de todos los pares
            orders_data = client.get_open_orders()
            query_type = "open_orders"
        
        # Convertir cada orden a modelo Pydantic
        orders = [FuturesOrder(**order) for order in orders_data]
        
        # Formatear la respuesta exitosa
        success_response = OrdersResponse(
            count=len(orders),
            query_type=query_type,
            symbol=symbol,
            orders=orders
        )
        return success_response.model_dump_json()
        
    except BinanceMCPError as e:
        error_response = ErrorResponse(
            error=True,
            code=e.code,
            message=e.message,
            details=e.details
        )
        return error_response.model_dump_json()
    except Exception as e:
        error_response = ErrorResponse(
            error=True,
            code="INTERNAL_SERVER_ERROR",
            message="Ocurrió un error inesperado al procesar la solicitud.",
            details=str(e)
        )
        return error_response.model_dump_json()


# --- Herramientas de Gestión de Órdenes ---

def _get_client():
    """Helper para validar credenciales y obtener el cliente."""
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    if not api_key or not api_secret:
        return None
    return BinanceClientFactory.create_client(api_key, api_secret)

def _missing_credentials_error() -> str:
    return ErrorResponse(
        error=True,
        code="MISSING_CREDENTIALS",
        message="Las credenciales de Binance no están configuradas en las variables de entorno."
    ).model_dump_json()

def _handle_error(e: Exception) -> str:
    if isinstance(e, BinanceMCPError):
        return ErrorResponse(error=True, code=e.code, message=e.message, details=e.details).model_dump_json()
    return ErrorResponse(error=True, code="INTERNAL_SERVER_ERROR", message="Ocurrió un error inesperado.", details=str(e)).model_dump_json()


@mcp.tool(annotations={"destructiveHint": True, "openWorldHint": True})
def create_order(
    symbol: str,
    side: str,
    type: str,
    positionSide: str,
    quantity: Optional[str] = None,
    price: Optional[str] = None,
    stopPrice: Optional[str] = None,
    timeInForce: Optional[str] = None,
    reduceOnly: Optional[bool] = None,
    closePosition: Optional[bool] = None,
    workingType: Optional[str] = None,
    newClientOrderId: Optional[str] = None,
) -> str:
    """
    Crea una nueva orden en Binance Futures.

    ⚠️ CONFIRMACIÓN REQUERIDA: Antes de ejecutar esta herramienta, SIEMPRE debes
    confirmar la acción con el usuario mostrando un resumen de la operación
    (símbolo, lado, tipo, cantidad, precio) y esperando su aprobación explícita.

    Parámetros obligatorios:
    - symbol: Par de trading (ej. BTCUSDT)
    - side: BUY o SELL
    - type: LIMIT, MARKET, STOP, STOP_MARKET, TAKE_PROFIT, TAKE_PROFIT_MARKET, TRAILING_STOP_MARKET
    - positionSide: LONG, SHORT o BOTH

    Parámetros condicionales según tipo:
    - LIMIT: requiere quantity, price, timeInForce
    - MARKET: requiere quantity
    - STOP/TAKE_PROFIT: requiere quantity, price, stopPrice
    - STOP_MARKET/TAKE_PROFIT_MARKET: requiere stopPrice (quantity opcional si closePosition=true)
    """
    client = _get_client()
    if not client:
        return _missing_credentials_error()

    try:
        params = {"symbol": symbol, "side": side, "type": type, "positionSide": positionSide}
        if quantity is not None:
            params["quantity"] = quantity
        if price is not None:
            params["price"] = price
        if stopPrice is not None:
            params["stopPrice"] = stopPrice
        if timeInForce is not None:
            params["timeInForce"] = timeInForce
        if reduceOnly is not None:
            params["reduceOnly"] = str(reduceOnly).lower()
        if closePosition is not None:
            params["closePosition"] = str(closePosition).lower()
        if workingType is not None:
            params["workingType"] = workingType
        if newClientOrderId is not None:
            params["newClientOrderId"] = newClientOrderId

        result = client.create_order(params)
        response = NewOrderResponse(**result)
        return response.model_dump_json()
    except Exception as e:
        return _handle_error(e)


@mcp.tool(annotations={"destructiveHint": True, "openWorldHint": True})
def create_batch_orders(orders: str) -> str:
    """
    Crea múltiples órdenes en Binance Futures en una sola invocación (máximo 5).

    ⚠️ CONFIRMACIÓN REQUERIDA: Antes de ejecutar esta herramienta, SIEMPRE debes
    confirmar la acción con el usuario mostrando un resumen de TODAS las órdenes
    y esperando su aprobación explícita.

    Parámetro:
    - orders: JSON string con lista de hasta 5 órdenes. Cada orden debe contener:
      symbol, side, type, positionSide, y parámetros adicionales según el tipo.

    Ejemplo: '[{"symbol":"BTCUSDT","side":"BUY","type":"LIMIT","positionSide":"LONG",
    "quantity":"0.001","price":"50000","timeInForce":"GTC"}]'
    """
    client = _get_client()
    if not client:
        return _missing_credentials_error()

    try:
        orders_list = json.loads(orders)
        if len(orders_list) > 5:
            return ErrorResponse(
                error=True, code="VALIDATION_ERROR",
                message="El máximo permitido es 5 órdenes por batch."
            ).model_dump_json()

        results_data = client.create_batch_orders(orders_list)
        results = []
        successful = 0
        failed = 0
        for item in results_data:
            if item.get("success"):
                successful += 1
                results.append(BatchOrderResult(success=True, order=NewOrderResponse(**item["order"])))
            else:
                failed += 1
                results.append(BatchOrderResult(
                    success=False,
                    error_code=item.get("error_code", "UNKNOWN"),
                    error_message=item.get("error_message", "Unknown error")
                ))

        response = BatchOrderResponse(total=len(results), successful=successful, failed=failed, results=results)
        return response.model_dump_json()
    except json.JSONDecodeError:
        return ErrorResponse(error=True, code="VALIDATION_ERROR", message="El parámetro 'orders' no es un JSON válido.").model_dump_json()
    except Exception as e:
        return _handle_error(e)


@mcp.tool(annotations={"destructiveHint": True, "openWorldHint": True})
def modify_order(
    symbol: str,
    side: str,
    quantity: str,
    price: str,
    orderId: Optional[int] = None,
    origClientOrderId: Optional[str] = None,
) -> str:
    """
    Modifica una orden LIMIT existente en Binance Futures.

    ⚠️ CONFIRMACIÓN REQUERIDA: Antes de ejecutar esta herramienta, SIEMPRE debes
    confirmar la acción con el usuario mostrando los cambios propuestos
    (nueva cantidad, nuevo precio) y esperando su aprobación explícita.

    Solo se pueden modificar órdenes de tipo LIMIT. La orden será reordenada
    en la cola de matching de Binance.

    Parámetros obligatorios: symbol, side, quantity, price.
    Identificación: al menos uno de orderId o origClientOrderId.
    """
    client = _get_client()
    if not client:
        return _missing_credentials_error()

    try:
        params = {"symbol": symbol, "side": side, "quantity": quantity, "price": price}
        if orderId is not None:
            params["orderId"] = orderId
        if origClientOrderId is not None:
            params["origClientOrderId"] = origClientOrderId

        result = client.modify_order(params)
        response = NewOrderResponse(**result)
        return response.model_dump_json()
    except Exception as e:
        return _handle_error(e)


@mcp.tool(annotations={"destructiveHint": True, "openWorldHint": True})
def modify_batch_orders(orders: str) -> str:
    """
    Modifica múltiples órdenes LIMIT en Binance Futures (máximo 5).

    ⚠️ CONFIRMACIÓN REQUERIDA: Antes de ejecutar esta herramienta, SIEMPRE debes
    confirmar la acción con el usuario mostrando un resumen de TODAS las
    modificaciones y esperando su aprobación explícita.

    Parámetro:
    - orders: JSON string con lista de hasta 5 modificaciones. Cada una debe
      contener: symbol, side, quantity, price, y orderId o origClientOrderId.

    Ejemplo: '[{"symbol":"BTCUSDT","side":"BUY","orderId":12345,"quantity":"0.002","price":"51000"}]'
    """
    client = _get_client()
    if not client:
        return _missing_credentials_error()

    try:
        orders_list = json.loads(orders)
        if len(orders_list) > 5:
            return ErrorResponse(
                error=True, code="VALIDATION_ERROR",
                message="El máximo permitido es 5 modificaciones por batch."
            ).model_dump_json()

        results_data = client.modify_batch_orders(orders_list)
        results = []
        successful = 0
        failed = 0
        for item in results_data:
            if item.get("success"):
                successful += 1
                results.append(BatchOrderResult(success=True, order=NewOrderResponse(**item["order"])))
            else:
                failed += 1
                results.append(BatchOrderResult(
                    success=False,
                    error_code=item.get("error_code", "UNKNOWN"),
                    error_message=item.get("error_message", "Unknown error")
                ))

        response = BatchOrderResponse(total=len(results), successful=successful, failed=failed, results=results)
        return response.model_dump_json()
    except json.JSONDecodeError:
        return ErrorResponse(error=True, code="VALIDATION_ERROR", message="El parámetro 'orders' no es un JSON válido.").model_dump_json()
    except Exception as e:
        return _handle_error(e)


@mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": True})
def get_order_modification_history(
    symbol: str,
    orderId: Optional[int] = None,
    origClientOrderId: Optional[str] = None,
    startTime: Optional[int] = None,
    endTime: Optional[int] = None,
    limit: Optional[int] = None,
) -> str:
    """
    Consulta el historial de modificaciones de órdenes en Binance Futures.

    El historial está disponible para un máximo de 3 meses.

    Parámetro obligatorio: symbol.
    Filtros opcionales: orderId, origClientOrderId, startTime, endTime, limit (default 50, máx 100).
    """
    client = _get_client()
    if not client:
        return _missing_credentials_error()

    try:
        params = {"symbol": symbol}
        if orderId is not None:
            params["orderId"] = orderId
        if origClientOrderId is not None:
            params["origClientOrderId"] = origClientOrderId
        if startTime is not None:
            params["startTime"] = startTime
        if endTime is not None:
            params["endTime"] = endTime
        if limit is not None:
            params["limit"] = limit

        results_data = client.get_order_modify_history(params)
        amendments = [OrderAmendment(
            amendment_id=item["amendment_id"],
            symbol=item["symbol"],
            order_id=item["order_id"],
            client_order_id=item["client_order_id"],
            time=item["time"],
            price_change=OrderAmendmentDetail(**item["price_change"]),
            qty_change=OrderAmendmentDetail(**item["qty_change"]),
            amendment_count=item["amendment_count"],
        ) for item in results_data]

        response = OrderAmendmentResponse(count=len(amendments), amendments=amendments)
        return response.model_dump_json()
    except Exception as e:
        return _handle_error(e)


@mcp.tool(annotations={"destructiveHint": True, "openWorldHint": True})
def cancel_order(
    symbol: str,
    orderId: Optional[int] = None,
    origClientOrderId: Optional[str] = None,
) -> str:
    """
    Cancela una orden activa en Binance Futures.

    ⚠️ CONFIRMACIÓN REQUERIDA: Antes de ejecutar esta herramienta, SIEMPRE debes
    confirmar la acción con el usuario indicando qué orden se va a cancelar
    y esperando su aprobación explícita.

    Parámetro obligatorio: symbol.
    Identificación: al menos uno de orderId o origClientOrderId.
    """
    client = _get_client()
    if not client:
        return _missing_credentials_error()

    try:
        result = client.cancel_order(symbol, order_id=orderId, orig_client_order_id=origClientOrderId)
        response = CancelOrderResponse(**result)
        return response.model_dump_json()
    except Exception as e:
        return _handle_error(e)


@mcp.tool(annotations={"destructiveHint": True, "openWorldHint": True})
def cancel_batch_orders(symbol: str, orderIdList: str) -> str:
    """
    Cancela múltiples órdenes en Binance Futures (máximo 10).

    ⚠️ CONFIRMACIÓN REQUERIDA: Antes de ejecutar esta herramienta, SIEMPRE debes
    confirmar la acción con el usuario mostrando las órdenes que se van a cancelar
    y esperando su aprobación explícita.

    Parámetros:
    - symbol: Par de trading (ej. BTCUSDT)
    - orderIdList: JSON string con lista de IDs de órdenes a cancelar (máx 10).
      Ejemplo: '[12345, 67890, 11111]'
    """
    client = _get_client()
    if not client:
        return _missing_credentials_error()

    try:
        id_list = json.loads(orderIdList)
        if len(id_list) > 10:
            return ErrorResponse(
                error=True, code="VALIDATION_ERROR",
                message="El máximo permitido es 10 órdenes por batch de cancelación."
            ).model_dump_json()

        results_data = client.cancel_batch_orders(symbol, id_list)
        results = []
        successful = 0
        failed = 0
        for item in results_data:
            if item.get("success"):
                successful += 1
                results.append(BatchOrderResult(success=True, order=NewOrderResponse(**item["order"])))
            else:
                failed += 1
                results.append(BatchOrderResult(
                    success=False,
                    error_code=item.get("error_code", "UNKNOWN"),
                    error_message=item.get("error_message", "Unknown error")
                ))

        response = BatchOrderResponse(total=len(results), successful=successful, failed=failed, results=results)
        return response.model_dump_json()
    except json.JSONDecodeError:
        return ErrorResponse(error=True, code="VALIDATION_ERROR", message="El parámetro 'orderIdList' no es un JSON válido.").model_dump_json()
    except Exception as e:
        return _handle_error(e)


@mcp.tool(annotations={"destructiveHint": True, "openWorldHint": True})
def cancel_all_open_orders(symbol: str) -> str:
    """
    Cancela TODAS las órdenes abiertas de un símbolo específico en Binance Futures.

    ⚠️ CONFIRMACIÓN REQUERIDA: Antes de ejecutar esta herramienta, SIEMPRE debes
    confirmar la acción con el usuario indicando que se cancelarán TODAS las órdenes
    abiertas del símbolo especificado y esperando su aprobación explícita.

    Parámetro obligatorio: symbol (ej. BTCUSDT).
    """
    client = _get_client()
    if not client:
        return _missing_credentials_error()

    try:
        result = client.cancel_all_open_orders(symbol)
        response = CancelAllOrdersResponse(**result)
        return response.model_dump_json()
    except Exception as e:
        return _handle_error(e)


# --- Herramientas de Consulta Avanzada de Órdenes y Trades ---

@mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": True})
def query_order(
    symbol: str,
    orderId: Optional[int] = None,
    origClientOrderId: Optional[str] = None,
) -> str:
    """
    Consulta el estado de una orden específica en Binance Futures.

    Se debe proporcionar obligatoriamente el símbolo y al menos uno de orderId o
    origClientOrderId. Órdenes CANCELED o EXPIRED sin trades ejecutados y con más
    de 3 días de antigüedad no estarán disponibles.

    Parámetro obligatorio: symbol.
    Identificación: al menos uno de orderId o origClientOrderId.
    """
    client = _get_client()
    if not client:
        return _missing_credentials_error()

    try:
        params = {"symbol": symbol}
        if orderId is not None:
            params["orderId"] = orderId
        if origClientOrderId is not None:
            params["origClientOrderId"] = origClientOrderId

        result = client.query_order(params)
        order = FuturesOrder(**result)
        response = OrdersResponse(count=1, query_type="query_order", symbol=symbol, orders=[order])
        return response.model_dump_json()
    except Exception as e:
        return _handle_error(e)


@mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": True})
def query_all_orders(
    symbol: str,
    orderId: Optional[int] = None,
    startTime: Optional[int] = None,
    endTime: Optional[int] = None,
    limit: Optional[int] = None,
) -> str:
    """
    Consulta el historial completo de órdenes (activas, canceladas, ejecutadas)
    de un símbolo en Binance Futures.

    El período de consulta temporal no puede exceder 7 días.
    Si startTime y endTime no se proporcionan, devuelve las órdenes más recientes.

    Parámetro obligatorio: symbol.
    Filtros opcionales: orderId (paginar desde un ID), startTime, endTime,
    limit (default 500, máx 1000).
    """
    client = _get_client()
    if not client:
        return _missing_credentials_error()

    try:
        params = {"symbol": symbol}
        if orderId is not None:
            params["orderId"] = orderId
        if startTime is not None:
            params["startTime"] = startTime
        if endTime is not None:
            params["endTime"] = endTime
        if limit is not None:
            params["limit"] = limit

        results = client.query_all_orders(params)
        orders = [FuturesOrder(**order) for order in results]
        response = OrdersResponse(count=len(orders), query_type="all_orders", symbol=symbol, orders=orders)
        return response.model_dump_json()
    except Exception as e:
        return _handle_error(e)


@mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": True})
def query_all_open_orders(
    symbol: Optional[str] = None,
) -> str:
    """
    Consulta todas las órdenes abiertas en Binance Futures.

    Si se proporciona symbol, filtra solo ese par (peso API: 1).
    Sin symbol, devuelve órdenes abiertas de todos los pares (peso API: 40).

    Parámetro opcional: symbol.
    """
    client = _get_client()
    if not client:
        return _missing_credentials_error()

    try:
        params = {}
        if symbol is not None:
            params["symbol"] = symbol

        results = client.query_all_open_orders(params)
        orders = [FuturesOrder(**order) for order in results]
        response = OrdersResponse(count=len(orders), query_type="open_orders", symbol=symbol, orders=orders)
        return response.model_dump_json()
    except Exception as e:
        return _handle_error(e)


@mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": True})
def query_current_open_order(
    symbol: str,
    orderId: Optional[int] = None,
    origClientOrderId: Optional[str] = None,
) -> str:
    """
    Consulta una orden abierta específica en Binance Futures.

    Se debe proporcionar obligatoriamente el símbolo y al menos uno de orderId o
    origClientOrderId. Si la orden no está abierta o no existe, devuelve un error.

    Parámetro obligatorio: symbol.
    Identificación: al menos uno de orderId o origClientOrderId.
    """
    client = _get_client()
    if not client:
        return _missing_credentials_error()

    try:
        params = {"symbol": symbol}
        if orderId is not None:
            params["orderId"] = orderId
        if origClientOrderId is not None:
            params["origClientOrderId"] = origClientOrderId

        result = client.query_current_open_order(params)
        if not result:
            return ErrorResponse(
                error=True, code="ORDER_NOT_FOUND",
                message=f"No se encontró una orden abierta con los identificadores proporcionados en {symbol}."
            ).model_dump_json()

        order = FuturesOrder(**result)
        response = OrdersResponse(count=1, query_type="current_open_order", symbol=symbol, orders=[order])
        return response.model_dump_json()
    except Exception as e:
        return _handle_error(e)


@mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": True})
def query_force_orders(
    symbol: Optional[str] = None,
    autoCloseType: Optional[str] = None,
    startTime: Optional[int] = None,
    endTime: Optional[int] = None,
    limit: Optional[int] = None,
) -> str:
    """
    Consulta el historial de órdenes de liquidación forzada en Binance Futures.

    Incluye órdenes de liquidación (LIQUIDATION) y auto-deleveraging (ADL).
    Solo están disponibles datos de los últimos 90 días.

    Parámetros opcionales:
    - symbol: Filtrar por par de trading.
    - autoCloseType: LIQUIDATION o ADL.
    - startTime, endTime: Rango temporal en milisegundos.
    - limit: Número máximo de resultados (default 50, máx 100).
    """
    client = _get_client()
    if not client:
        return _missing_credentials_error()

    try:
        params = {}
        if symbol is not None:
            params["symbol"] = symbol
        if autoCloseType is not None:
            params["autoCloseType"] = autoCloseType
        if startTime is not None:
            params["startTime"] = startTime
        if endTime is not None:
            params["endTime"] = endTime
        if limit is not None:
            params["limit"] = limit

        results = client.query_force_orders(params)
        orders = [FuturesOrder(**order) for order in results]
        response = ForceOrdersResponse(count=len(orders), orders=orders)
        return response.model_dump_json()
    except Exception as e:
        return _handle_error(e)


@mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": True})
def query_trade_list(
    symbol: str,
    orderId: Optional[int] = None,
    startTime: Optional[int] = None,
    endTime: Optional[int] = None,
    fromId: Optional[int] = None,
    limit: Optional[int] = None,
) -> str:
    """
    Consulta el historial de ejecuciones (trades) de un símbolo en Binance Futures.

    Cada trade incluye: precio, cantidad, comisión, PnL realizado, timestamp, y más.
    Solo están disponibles datos de los últimos 6 meses.

    Parámetro obligatorio: symbol.
    Filtros opcionales:
    - orderId: Obtener trades de una orden específica.
    - startTime, endTime: Rango temporal en milisegundos.
    - fromId: Paginar desde un trade ID específico.
    - limit: Número máximo de resultados (default 500, máx 1000).
    """
    client = _get_client()
    if not client:
        return _missing_credentials_error()

    try:
        params = {"symbol": symbol}
        if orderId is not None:
            params["orderId"] = orderId
        if startTime is not None:
            params["startTime"] = startTime
        if endTime is not None:
            params["endTime"] = endTime
        if fromId is not None:
            params["fromId"] = fromId
        if limit is not None:
            params["limit"] = limit

        results = client.query_trade_list(params)
        trades = [TradeRecord(**trade) for trade in results]
        response = TradeListResponse(count=len(trades), symbol=symbol, trades=trades)
        return response.model_dump_json()
    except Exception as e:
        return _handle_error(e)


def main():
    mcp.run()

if __name__ == "__main__":
    main()

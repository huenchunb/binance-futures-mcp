from pydantic import BaseModel, Field
from typing import Optional, List

class USDTBalance(BaseModel):
    asset: str = Field(default="USDT", description="El activo consultado (siempre USDT)")
    balance: str = Field(description="Saldo total en la cuenta de futuros")
    available_balance: str = Field(description="Saldo disponible para nuevas posiciones (withdrawAvailable)")
    
class ErrorResponse(BaseModel):
    error: bool = Field(default=True, description="Indicador de que ocurrió un error")
    code: str = Field(description="Código del error interno o de la API")
    message: str = Field(description="Mensaje descriptivo del error")
    details: Optional[str] = Field(default=None, description="Detalles adicionales del error")

class FuturesPosition(BaseModel):
    symbol: str = Field(description="Par de trading (ej. BTCUSDT)")
    position_side: str = Field(description="Lado de la posición: BOTH, LONG, SHORT")
    position_amount: str = Field(description="Cantidad de la posición (positivo=long, negativo=short)")
    entry_price: str = Field(description="Precio promedio de entrada")
    break_even_price: str = Field(default="0.0", description="Precio de break-even incluyendo fees")
    mark_price: str = Field(description="Precio de marca actual")
    liquidation_price: str = Field(description="Precio estimado de liquidación")
    leverage: str = Field(description="Apalancamiento configurado")
    unrealized_profit: str = Field(description="PnL no realizado")
    margin_type: str = Field(description="Tipo de margen: isolated o cross")
    initial_margin: str = Field(description="Margen inicial requerido")
    maint_margin: str = Field(description="Margen de mantenimiento")
    notional: str = Field(description="Valor nocional de la posición")
    isolated_margin: str = Field(default="0.0", description="Margen aislado asignado (si aplica)")
    update_time: int = Field(description="Timestamp de la última actualización")

class OpenPositionsResponse(BaseModel):
    count: int = Field(description="Número de posiciones abiertas encontradas")
    positions: List[FuturesPosition] = Field(description="Lista de posiciones abiertas")

class FuturesOrder(BaseModel):
    order_id: int = Field(description="ID único de la orden asignado por Binance")
    symbol: str = Field(description="Par de trading (ej. BTCUSDT)")
    type: str = Field(description="Tipo de orden (LIMIT, STOP_MARKET, TAKE_PROFIT_MARKET, TRAILING_STOP_MARKET, etc.)")
    side: str = Field(description="Lado de la orden: BUY o SELL")
    position_side: str = Field(description="Lado de la posición: BOTH, LONG, SHORT")
    status: str = Field(description="Estado de la orden (NEW, FILLED, CANCELED, EXPIRED, etc.)")
    price: str = Field(description="Precio de la orden")
    stop_price: str = Field(default="0", description="Precio de activación para órdenes Stop Loss / Take Profit")
    orig_qty: str = Field(description="Cantidad original solicitada")
    executed_qty: str = Field(default="0", description="Cantidad ejecutada hasta el momento")
    avg_price: str = Field(default="0", description="Precio promedio de ejecución")
    reduce_only: bool = Field(default=False, description="Si la orden es de tipo reduce-only")
    close_position: bool = Field(default=False, description="Si la orden cierra la posición completa")
    time_in_force: str = Field(default="GTC", description="Validez temporal de la orden (GTC, IOC, FOK, GTX)")
    working_type: str = Field(default="CONTRACT_PRICE", description="Tipo de precio de trabajo (CONTRACT_PRICE, MARK_PRICE)")
    time: int = Field(description="Timestamp de creación de la orden")
    update_time: int = Field(description="Timestamp de la última actualización de la orden")

class OrdersResponse(BaseModel):
    count: int = Field(description="Número de órdenes devueltas")
    query_type: str = Field(description="Tipo de consulta realizada: 'open_orders' u 'all_orders'")
    symbol: Optional[str] = Field(default=None, description="Símbolo consultado (solo cuando se consulta historial por par)")
    orders: List[FuturesOrder] = Field(description="Lista de órdenes")

# --- Modelos de Response para Gestión de Órdenes ---

class NewOrderResponse(BaseModel):
    order_id: int = Field(description="ID único de la orden asignado por Binance")
    client_order_id: str = Field(default="", description="ID de la orden asignado por el cliente")
    symbol: str = Field(description="Par de trading (ej. BTCUSDT)")
    status: str = Field(description="Estado de la orden (NEW, FILLED, PARTIALLY_FILLED, etc.)")
    type: str = Field(description="Tipo de orden (LIMIT, MARKET, STOP_MARKET, etc.)")
    side: str = Field(description="Lado de la orden: BUY o SELL")
    position_side: str = Field(default="BOTH", description="Lado de la posición: BOTH, LONG, SHORT")
    price: str = Field(default="0", description="Precio de la orden")
    orig_qty: str = Field(default="0", description="Cantidad original solicitada")
    executed_qty: str = Field(default="0", description="Cantidad ejecutada hasta el momento")
    avg_price: str = Field(default="0", description="Precio promedio de ejecución")
    stop_price: str = Field(default="0", description="Precio de activación (Stop Loss / Take Profit)")
    time_in_force: str = Field(default="GTC", description="Validez temporal de la orden")
    working_type: str = Field(default="CONTRACT_PRICE", description="Tipo de precio de trabajo")
    reduce_only: bool = Field(default=False, description="Si la orden es reduce-only")
    close_position: bool = Field(default=False, description="Si la orden cierra la posición completa")
    update_time: int = Field(default=0, description="Timestamp de la última actualización")

class BatchOrderResult(BaseModel):
    success: bool = Field(description="Si la operación individual fue exitosa")
    order: Optional[NewOrderResponse] = Field(default=None, description="Datos de la orden (solo si éxito)")
    error_code: Optional[str] = Field(default=None, description="Código de error (solo si fallo)")
    error_message: Optional[str] = Field(default=None, description="Mensaje de error (solo si fallo)")

class BatchOrderResponse(BaseModel):
    total: int = Field(description="Número total de órdenes procesadas")
    successful: int = Field(description="Número de órdenes exitosas")
    failed: int = Field(description="Número de órdenes fallidas")
    results: List[BatchOrderResult] = Field(description="Resultado individual de cada orden")

class OrderAmendmentDetail(BaseModel):
    before: str = Field(description="Valor antes de la modificación")
    after: str = Field(description="Valor después de la modificación")

class OrderAmendment(BaseModel):
    amendment_id: int = Field(description="ID único de la modificación")
    symbol: str = Field(description="Par de trading")
    order_id: int = Field(description="ID de la orden modificada")
    client_order_id: str = Field(default="", description="ID del cliente de la orden")
    time: int = Field(description="Timestamp de la modificación")
    price_change: OrderAmendmentDetail = Field(description="Cambio en el precio (antes/después)")
    qty_change: OrderAmendmentDetail = Field(description="Cambio en la cantidad (antes/después)")
    amendment_count: int = Field(description="Número total de modificaciones realizadas a esta orden")

class OrderAmendmentResponse(BaseModel):
    count: int = Field(description="Número de registros de modificación devueltos")
    amendments: List[OrderAmendment] = Field(description="Lista de modificaciones")

class CancelOrderResponse(BaseModel):
    order_id: int = Field(description="ID de la orden cancelada")
    client_order_id: str = Field(default="", description="ID del cliente de la orden")
    symbol: str = Field(description="Par de trading")
    status: str = Field(description="Estado de la orden (CANCELED)")
    type: str = Field(description="Tipo de orden")
    side: str = Field(description="Lado de la orden: BUY o SELL")
    position_side: str = Field(default="BOTH", description="Lado de la posición")
    price: str = Field(default="0", description="Precio de la orden")
    orig_qty: str = Field(default="0", description="Cantidad original")
    executed_qty: str = Field(default="0", description="Cantidad ejecutada")
    avg_price: str = Field(default="0", description="Precio promedio de ejecución")
    stop_price: str = Field(default="0", description="Precio de activación")
    update_time: int = Field(default=0, description="Timestamp de la actualización")

class CancelAllOrdersResponse(BaseModel):
    code: int = Field(description="Código de respuesta de Binance (200 = éxito)")
    message: str = Field(description="Mensaje de respuesta")

# --- Modelos para Consultas Avanzadas de Órdenes y Trades ---

class TradeRecord(BaseModel):
    id: int = Field(description="ID único del trade")
    symbol: str = Field(description="Par de trading (ej. BTCUSDT)")
    order_id: int = Field(description="ID de la orden que generó este trade")
    side: str = Field(description="Lado del trade: BUY o SELL")
    price: str = Field(description="Precio de ejecución del trade")
    qty: str = Field(description="Cantidad ejecutada en el trade")
    realized_pnl: str = Field(default="0", description="PnL realizado en este trade")
    quote_qty: str = Field(default="0", description="Cantidad en moneda cotizada (USDT)")
    commission: str = Field(default="0", description="Comisión cobrada por el trade")
    commission_asset: str = Field(default="USDT", description="Activo en el que se cobró la comisión")
    time: int = Field(description="Timestamp del trade en milisegundos")
    buyer: bool = Field(description="Si el trade fue como comprador")
    maker: bool = Field(description="Si el trade fue como maker (no taker)")
    position_side: str = Field(default="BOTH", description="Lado de la posición: BOTH, LONG, SHORT")

class TradeListResponse(BaseModel):
    count: int = Field(description="Número de trades devueltos")
    symbol: str = Field(description="Símbolo consultado")
    trades: List[TradeRecord] = Field(description="Lista de trades ejecutados")

class ForceOrdersResponse(BaseModel):
    count: int = Field(description="Número de órdenes de liquidación forzada devueltas")
    orders: List[FuturesOrder] = Field(description="Lista de órdenes de liquidación forzada")


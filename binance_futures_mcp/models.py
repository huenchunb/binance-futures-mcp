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


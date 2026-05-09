from pydantic import BaseModel, Field
from typing import Optional

class USDTBalance(BaseModel):
    asset: str = Field(default="USDT", description="El activo consultado (siempre USDT)")
    balance: str = Field(description="Saldo total en la cuenta de futuros")
    available_balance: str = Field(description="Saldo disponible para nuevas posiciones (withdrawAvailable)")
    
class ErrorResponse(BaseModel):
    error: bool = Field(default=True, description="Indicador de que ocurrió un error")
    code: str = Field(description="Código del error interno o de la API")
    message: str = Field(description="Mensaje descriptivo del error")
    details: Optional[str] = Field(default=None, description="Detalles adicionales del error")

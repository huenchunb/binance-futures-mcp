import os
import json
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from binance_futures_mcp.binance_client.factory import BinanceClientFactory
from binance_futures_mcp.errors import BinanceMCPError
from binance_futures_mcp.models import USDTBalance, ErrorResponse, FuturesPosition, OpenPositionsResponse

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

def main():
    mcp.run()

if __name__ == "__main__":
    main()


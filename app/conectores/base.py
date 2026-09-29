from datetime import date
from typing import Protocol

from pydantic import SecretStr

from ..modelos import DatosTributarios


class ErrorAutenticacion(Exception):
    """RUT o clave rechazados por el SII / proveedor."""


class ConectorSII(Protocol):
    nombre: str

    def obtener_datos(self, rut: str, clave: SecretStr, hoy: date) -> DatosTributarios:
        """Trae los datos del contribuyente. La clave solo se usa aquí y no se guarda."""
        ...

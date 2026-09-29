"""Conectores que obtienen los datos del SII. La app solo depende de la interfaz."""

import os

from .base import ConectorSII, ErrorAutenticacion
from .simulado import ConectorSimulado


def obtener_conector() -> ConectorSII:
    """Elige el conector según la variable CONECTOR_SII (por ahora solo 'simulado')."""
    nombre = os.environ.get("CONECTOR_SII", "simulado")
    if nombre == "simulado":
        return ConectorSimulado()
    raise ValueError(f"Conector desconocido: {nombre}")


__all__ = ["ConectorSII", "ErrorAutenticacion", "obtener_conector"]

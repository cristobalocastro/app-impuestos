"""API local: recibe RUT y clave, trae los datos y devuelve la revisión.

La clave nunca se guarda ni se escribe en logs: llega como SecretStr, se pasa
al conector y se descarta al terminar la petición.
"""

from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, SecretStr

from . import rut as rut_util
from .conectores import ErrorAutenticacion, obtener_conector
from .modelos import ResultadoRevision
from .revision import revisar

STATIC = Path(__file__).parent / "static"

app = FastAPI(title="Revisión de impuestos", docs_url=None, redoc_url=None)


@app.exception_handler(RequestValidationError)
def error_validacion(_: Request, exc: RequestValidationError) -> JSONResponse:
    # La respuesta por defecto repite el cuerpo recibido, que puede incluir la clave.
    campos = [".".join(str(p) for p in e["loc"][1:]) for e in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": f"Datos inválidos: {', '.join(campos)}"})


class SolicitudRevision(BaseModel):
    rut: str
    clave: SecretStr


@app.get("/", include_in_schema=False)
def inicio() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.post("/api/revision", response_model=ResultadoRevision)
def crear_revision(solicitud: SolicitudRevision) -> ResultadoRevision:
    if not rut_util.es_valido(solicitud.rut):
        raise HTTPException(status_code=422, detail="El RUT no es válido.")
    conector = obtener_conector()
    hoy = date.today()
    try:
        datos = conector.obtener_datos(solicitud.rut, solicitud.clave, hoy)
    except ErrorAutenticacion:
        raise HTTPException(status_code=401, detail="RUT o clave incorrectos.")
    return revisar(datos, hoy, fuente=conector.nombre)

"""Datos tributarios normalizados, independientes del proveedor que los entrega."""

from datetime import date
from enum import Enum

from pydantic import BaseModel


class Contribuyente(BaseModel):
    rut: str
    nombre: str
    actividades: list[str]
    inicio_actividades: date | None = None


class ResumenMensualRCV(BaseModel):
    """Totales del Registro de Compras y Ventas de un mes (periodo = 'AAAA-MM')."""

    periodo: str
    ventas_neto: int
    iva_debito: int
    compras_neto: int
    iva_credito: int


class EstadoF29(str, Enum):
    presentado = "presentado"
    no_presentado = "no_presentado"


class F29(BaseModel):
    periodo: str
    estado: EstadoF29
    iva_debito_declarado: int = 0
    iva_credito_declarado: int = 0
    total_pagado: int = 0


class FacturaPendiente(BaseModel):
    """Factura de compra recibida que aún no se acepta ni reclama."""

    folio: int
    emisor: str
    monto_total: int
    fecha_recepcion: date


class BoletaHonorarios(BaseModel):
    folio: int
    fecha: date
    bruto: int
    retencion: int
    emitida: bool  # True = la emití yo; False = la recibí


class EstadoF22(str, Enum):
    sin_declarar = "sin_declarar"
    aceptada = "aceptada"
    observada = "observada"
    devolucion_pendiente = "devolucion_pendiente"
    giro_por_pagar = "giro_por_pagar"


class F22(BaseModel):
    anio_tributario: int
    estado: EstadoF22
    monto: int = 0  # devolución (positivo) o pago (negativo)
    observaciones: list[str] = []


class DeudaTGR(BaseModel):
    concepto: str
    monto: int
    vencimiento: date


class DatosTributarios(BaseModel):
    contribuyente: Contribuyente
    rcv: list[ResumenMensualRCV]
    f29: list[F29]
    facturas_pendientes: list[FacturaPendiente]
    honorarios: list[BoletaHonorarios]
    f22: F22 | None
    deudas_tgr: list[DeudaTGR]


class Severidad(str, Enum):
    alta = "alta"
    media = "media"
    info = "info"


class Alerta(BaseModel):
    codigo: str
    severidad: Severidad
    titulo: str
    detalle: str


class ResultadoRevision(BaseModel):
    contribuyente: Contribuyente
    fecha_revision: date
    fuente: str
    alertas: list[Alerta]
    resumen: dict[str, int]

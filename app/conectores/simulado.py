"""Datos de prueba realistas para desarrollar sin tocar el SII ni usar claves reales.

Acepta solo el RUT 11.111.111-1 con la clave 'demo'. Los datos traen problemas
a propósito para que cada revisión tenga algo que mostrar.
"""

from datetime import date, timedelta

from pydantic import SecretStr

from .. import rut as rut_util
from ..modelos import (
    F22,
    F29,
    BoletaHonorarios,
    Contribuyente,
    DatosTributarios,
    DeudaTGR,
    EstadoF22,
    EstadoF29,
    FacturaPendiente,
    ResumenMensualRCV,
)
from ..periodos import ultimos_periodos
from .base import ErrorAutenticacion

RUT_DEMO = "111111111"
CLAVE_DEMO = "demo"


class ConectorSimulado:
    nombre = "simulado"

    def obtener_datos(self, rut: str, clave: SecretStr, hoy: date) -> DatosTributarios:
        if rut_util.limpiar(rut) != RUT_DEMO or clave.get_secret_value() != CLAVE_DEMO:
            raise ErrorAutenticacion("RUT o clave incorrectos")

        periodos = ultimos_periodos(hoy, 12)
        rcv, f29 = [], []
        for i, periodo in enumerate(periodos):
            ventas = 2_000_000 + i * 150_000
            compras = 800_000 + i * 50_000
            debito, credito = round(ventas * 0.19), round(compras * 0.19)
            rcv.append(ResumenMensualRCV(
                periodo=periodo, ventas_neto=ventas, iva_debito=debito,
                compras_neto=compras, iva_credito=credito,
            ))
            if i == 8:
                # Mes sin declarar
                f29.append(F29(periodo=periodo, estado=EstadoF29.no_presentado))
            elif i == 10:
                # Débito declarado menor que el del RCV
                f29.append(F29(
                    periodo=periodo, estado=EstadoF29.presentado,
                    iva_debito_declarado=debito - 95_000, iva_credito_declarado=credito,
                    total_pagado=debito - 95_000 - credito,
                ))
            else:
                f29.append(F29(
                    periodo=periodo, estado=EstadoF29.presentado,
                    iva_debito_declarado=debito, iva_credito_declarado=credito,
                    total_pagado=debito - credito,
                ))

        return DatosTributarios(
            contribuyente=Contribuyente(
                rut=rut_util.formatear(RUT_DEMO),
                nombre="Contribuyente de Prueba",
                actividades=["Servicios de consultoría informática", "Asesorías profesionales"],
                inicio_actividades=date(2019, 3, 1),
            ),
            rcv=rcv,
            f29=f29,
            facturas_pendientes=[
                FacturaPendiente(folio=48213, emisor="Proveedor Uno SpA", monto_total=595_000,
                                 fecha_recepcion=hoy - timedelta(days=6)),
                FacturaPendiente(folio=1177, emisor="Servicios Dos Ltda.", monto_total=119_000,
                                 fecha_recepcion=hoy - timedelta(days=1)),
            ],
            honorarios=[
                BoletaHonorarios(folio=n, fecha=hoy - timedelta(days=30 * n), bruto=500_000,
                                 retencion=76_250, emitida=True)
                for n in range(1, 5)
            ],
            f22=F22(
                anio_tributario=hoy.year, estado=EstadoF22.observada, monto=184_000,
                observaciones=["Diferencia en retenciones de honorarios informadas por terceros"],
            ),
            deudas_tgr=[
                DeudaTGR(concepto=f"IVA período {periodos[8]}", monto=412_300,
                         vencimiento=hoy - timedelta(days=45)),
            ],
        )

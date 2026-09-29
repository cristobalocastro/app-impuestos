"""Reglas que revisan los datos tributarios y generan alertas."""

from datetime import date

from .modelos import (
    Alerta,
    DatosTributarios,
    EstadoF22,
    EstadoF29,
    ResultadoRevision,
    Severidad,
)

# El SII da 8 días corridos para aceptar o reclamar una factura recibida.
PLAZO_RECLAMO_DIAS = 8
# Diferencias de IVA menores a esto se consideran redondeo.
TOLERANCIA_IVA = 1_000


def _clp(monto: int) -> str:
    return "$" + f"{monto:,}".replace(",", ".")


def revisar_f29(datos: DatosTributarios) -> list[Alerta]:
    alertas = []
    rcv = {r.periodo: r for r in datos.rcv}
    for f in datos.f29:
        mes = rcv.get(f.periodo)
        if f.estado == EstadoF29.no_presentado:
            detalle = "No hay F29 presentado para este período."
            if mes and mes.ventas_neto > 0:
                detalle += f" Tuviste ventas netas por {_clp(mes.ventas_neto)} (IVA débito {_clp(mes.iva_debito)})."
            alertas.append(Alerta(
                codigo="F29_NO_PRESENTADO", severidad=Severidad.alta,
                titulo=f"F29 sin presentar: {f.periodo}", detalle=detalle,
            ))
            continue
        if not mes:
            continue
        dif_debito = mes.iva_debito - f.iva_debito_declarado
        if abs(dif_debito) > TOLERANCIA_IVA:
            alertas.append(Alerta(
                codigo="F29_DIFERENCIA_DEBITO", severidad=Severidad.alta,
                titulo=f"IVA débito no cuadra: {f.periodo}",
                detalle=(f"El Registro de Ventas suma {_clp(mes.iva_debito)} de IVA, pero el F29 declara "
                         f"{_clp(f.iva_debito_declarado)} (diferencia {_clp(dif_debito)})."),
            ))
        dif_credito = mes.iva_credito - f.iva_credito_declarado
        if abs(dif_credito) > TOLERANCIA_IVA:
            alertas.append(Alerta(
                codigo="F29_DIFERENCIA_CREDITO", severidad=Severidad.media,
                titulo=f"IVA crédito no cuadra: {f.periodo}",
                detalle=(f"El Registro de Compras suma {_clp(mes.iva_credito)} de IVA, pero el F29 declara "
                         f"{_clp(f.iva_credito_declarado)} (diferencia {_clp(dif_credito)})."),
            ))
    return alertas


def revisar_facturas_pendientes(datos: DatosTributarios, hoy: date) -> list[Alerta]:
    alertas = []
    for fac in datos.facturas_pendientes:
        dias = (hoy - fac.fecha_recepcion).days
        restantes = PLAZO_RECLAMO_DIAS - dias
        if restantes < 0:
            continue  # ya quedó aceptada tácitamente
        alertas.append(Alerta(
            codigo="FACTURA_POR_ACEPTAR",
            severidad=Severidad.media if restantes <= 3 else Severidad.info,
            titulo=f"Factura {fac.folio} de {fac.emisor} por aceptar o reclamar",
            detalle=(f"Monto {_clp(fac.monto_total)}. Te quedan {restantes} día(s) para reclamarla; "
                     "después se entiende aceptada."),
        ))
    return alertas


def revisar_f22(datos: DatosTributarios) -> list[Alerta]:
    f22 = datos.f22
    if not f22:
        return []
    anio = f22.anio_tributario
    if f22.estado == EstadoF22.observada:
        obs = " ".join(f22.observaciones) or "Revisa el detalle en el sitio del SII."
        return [Alerta(codigo="F22_OBSERVADA", severidad=Severidad.alta,
                       titulo=f"Declaración de renta {anio} observada", detalle=obs)]
    if f22.estado == EstadoF22.giro_por_pagar:
        return [Alerta(codigo="F22_GIRO", severidad=Severidad.alta,
                       titulo=f"Renta {anio}: tienes un pago pendiente",
                       detalle=f"Monto a pagar {_clp(abs(f22.monto))}.")]
    if f22.estado == EstadoF22.devolucion_pendiente:
        return [Alerta(codigo="F22_DEVOLUCION", severidad=Severidad.info,
                       titulo=f"Renta {anio}: devolución en proceso",
                       detalle=f"Monto a devolver {_clp(f22.monto)}.")]
    if f22.estado == EstadoF22.sin_declarar:
        return [Alerta(codigo="F22_SIN_DECLARAR", severidad=Severidad.alta,
                       titulo=f"Renta {anio} sin declarar",
                       detalle="No hay declaración de renta presentada para este año.")]
    return []


def revisar_deudas(datos: DatosTributarios, hoy: date) -> list[Alerta]:
    return [
        Alerta(codigo="DEUDA_TGR_VENCIDA", severidad=Severidad.alta,
               titulo=f"Deuda vencida en Tesorería: {d.concepto}",
               detalle=f"{_clp(d.monto)}, vencida hace {(hoy - d.vencimiento).days} días. Genera intereses y multas.")
        for d in datos.deudas_tgr if d.vencimiento < hoy
    ]


def revisar_honorarios(datos: DatosTributarios, hoy: date) -> list[Alerta]:
    del_anio = [b for b in datos.honorarios if b.emitida and b.fecha.year == hoy.year]
    if not del_anio:
        return []
    bruto = sum(b.bruto for b in del_anio)
    retencion = sum(b.retencion for b in del_anio)
    return [Alerta(
        codigo="HONORARIOS_RESUMEN", severidad=Severidad.info,
        titulo=f"Boletas de honorarios {hoy.year}",
        detalle=(f"Emitiste {len(del_anio)} boleta(s) por {_clp(bruto)} bruto, con {_clp(retencion)} retenido. "
                 "Esa retención se descuenta en tu próxima declaración de renta."),
    )]


ORDEN_SEVERIDAD = {Severidad.alta: 0, Severidad.media: 1, Severidad.info: 2}


def revisar(datos: DatosTributarios, hoy: date, fuente: str) -> ResultadoRevision:
    alertas = (
        revisar_f29(datos)
        + revisar_facturas_pendientes(datos, hoy)
        + revisar_f22(datos)
        + revisar_deudas(datos, hoy)
        + revisar_honorarios(datos, hoy)
    )
    alertas.sort(key=lambda a: ORDEN_SEVERIDAD[a.severidad])
    resumen = {s.value: sum(1 for a in alertas if a.severidad == s) for s in Severidad}
    return ResultadoRevision(
        contribuyente=datos.contribuyente, fecha_revision=hoy, fuente=fuente,
        alertas=alertas, resumen=resumen,
    )

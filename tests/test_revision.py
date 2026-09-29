from datetime import date

from pydantic import SecretStr

from app.conectores.simulado import ConectorSimulado
from app.periodos import ultimos_periodos
from app.revision import revisar

HOY = date(2026, 9, 29)


def _resultado():
    datos = ConectorSimulado().obtener_datos("11.111.111-1", SecretStr("demo"), HOY)
    return revisar(datos, HOY, fuente="simulado")


def _codigos(r):
    return [a.codigo for a in r.alertas]


def test_periodos():
    p = ultimos_periodos(date(2026, 1, 15), 3)
    assert p == ["2025-10", "2025-11", "2025-12"]


def test_detecta_f29_no_presentado_y_diferencia():
    r = _resultado()
    assert _codigos(r).count("F29_NO_PRESENTADO") == 1
    assert _codigos(r).count("F29_DIFERENCIA_DEBITO") == 1
    assert "F29_DIFERENCIA_CREDITO" not in _codigos(r)


def test_detecta_resto_de_alertas():
    codigos = _codigos(_resultado())
    for esperado in ["FACTURA_POR_ACEPTAR", "F22_OBSERVADA", "DEUDA_TGR_VENCIDA", "HONORARIOS_RESUMEN"]:
        assert esperado in codigos


def test_alertas_ordenadas_por_severidad():
    r = _resultado()
    orden = {"alta": 0, "media": 1, "info": 2}
    sev = [orden[a.severidad.value] for a in r.alertas]
    assert sev == sorted(sev)
    assert sum(r.resumen.values()) == len(r.alertas)


def test_factura_fuera_de_plazo_no_alerta():
    datos = ConectorSimulado().obtener_datos("111111111", SecretStr("demo"), HOY)
    r = revisar(datos, date(2026, 10, 30), fuente="simulado")
    assert "FACTURA_POR_ACEPTAR" not in _codigos(r)

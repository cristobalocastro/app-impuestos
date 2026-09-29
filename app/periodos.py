from datetime import date


def ultimos_periodos(hoy: date, n: int) -> list[str]:
    """Los n meses anteriores al mes actual, del más antiguo al más reciente ('AAAA-MM')."""
    anio, mes = hoy.year, hoy.month
    periodos = []
    for _ in range(n):
        mes -= 1
        if mes == 0:
            anio, mes = anio - 1, 12
        periodos.append(f"{anio:04d}-{mes:02d}")
    return list(reversed(periodos))

# Revisión de impuestos

App personal que revisa tu situación tributaria en el SII (Chile): ingresas tu RUT y clave, y te muestra alertas sobre F29, IVA, facturas por aceptar, declaración de renta y deudas en Tesorería.

Corre en tu propio computador. **La clave no se guarda**: se usa para esa revisión y se descarta.

## Cómo usarla

Requiere Python 3.11 o superior.

```bash
python3 -m venv .venv
source .venv/bin/activate          # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Abre http://127.0.0.1:8000 en tu navegador.

Por ahora la app usa **datos simulados**: entra con el RUT `11.111.111-1` y la clave `demo`. Todavía no se conecta al SII real; ese paso requiere elegir un proveedor de datos (Floid o SimpleAPI) y agregar su conector.

## Qué revisa

| Revisión | Alerta |
|---|---|
| F29 de los últimos 12 meses | Meses sin declarar; IVA débito o crédito que no cuadra con el Registro de Compras y Ventas |
| Facturas de compra recibidas | Facturas por aceptar o reclamar dentro del plazo de 8 días |
| Declaración de renta (F22) | Observada, sin declarar, con pago pendiente o devolución en proceso |
| Tesorería (TGR) | Deudas vencidas |
| Boletas de honorarios | Resumen del año y retención acumulada |

## Estructura

```
app/
  main.py            API local y página web
  revision.py        Reglas que generan las alertas
  modelos.py         Datos tributarios normalizados
  rut.py             Validación de RUT
  conectores/
    base.py          Interfaz que debe cumplir cualquier fuente de datos
    simulado.py      Datos de prueba (sin SII real)
  static/index.html  Interfaz
tests/
```

Para conectar el SII real se agrega un conector nuevo en `app/conectores/` que cumpla la interfaz de `base.py`, y se elige con la variable de entorno `CONECTOR_SII`.

## Seguridad de la clave

- La clave viaja solo a `127.0.0.1` (tu computador) y de ahí al proveedor.
- Se maneja como `SecretStr`: no aparece en logs, errores ni respuestas.
- No se escribe en disco ni en base de datos.

## Pruebas

```bash
pip install -r requirements-dev.txt
pytest
```

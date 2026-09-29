from fastapi.testclient import TestClient

from app.main import app

cliente = TestClient(app)


def test_pagina_inicio():
    assert cliente.get("/").status_code == 200


def test_revision_ok():
    r = cliente.post("/api/revision", json={"rut": "11.111.111-1", "clave": "demo"})
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["contribuyente"]["rut"] == "11.111.111-1"
    assert cuerpo["alertas"]


def test_clave_incorrecta():
    r = cliente.post("/api/revision", json={"rut": "11.111.111-1", "clave": "otra"})
    assert r.status_code == 401


def test_rut_invalido():
    r = cliente.post("/api/revision", json={"rut": "11.111.111-2", "clave": "demo"})
    assert r.status_code == 422


def test_error_de_validacion_no_repite_la_clave():
    r = cliente.post("/api/revision", json={"clave": "mi-clave-secreta"})
    assert r.status_code == 422
    assert "mi-clave-secreta" not in r.text

from app import rut


def test_rut_valido():
    assert rut.es_valido("11.111.111-1")
    assert rut.es_valido("12345678-5")
    assert rut.es_valido("10000013-K")


def test_rut_invalido():
    assert not rut.es_valido("11.111.111-2")
    assert not rut.es_valido("abc")
    assert not rut.es_valido("")


def test_formatear():
    assert rut.formatear("111111111") == "11.111.111-1"

import pytest
from app.database import Database

def test_humo_contratos_sin_500(client):
    """Verifica que la ruta de contratos no arroje error 500 sin sesión activa."""
    resp = client.get("/contratos/")
    assert resp.status_code != 500
    assert resp.status_code in [200, 302, 401, 403]


def test_humo_dashboard_contratos_carga(client, superadmin):
    """Verifica que la vista principal de contratos cargue correctamente con sesión."""
    response = client.get("/contratos/")
    assert response.status_code == 200
    assert b"contrato" in response.data.lower()


def test_humo_consulta_basica_contratos(client, superadmin):
    """Verifica que el endpoint de consulta de contratos responda 200 y retorne una lista JSON."""
    resp = client.post("/contratos/", data={"consultar": "1"})
    assert resp.status_code == 200
    assert resp.is_json
    assert isinstance(resp.get_json(), list)


#pytest -W ignore tests/humo/test_contrato_humo.py

#pytest -W ignore  tests/humo/test_patrocinador_humo.py  -v -s -o addopts="" 

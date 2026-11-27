import pytest

def test_humo_patrocinador_sin_500(client):
    resp = client.get("/patrocinador/")
    assert resp.status_code != 500
    assert resp.status_code in [200, 302, 401, 403]


def test_humo_dashboard_patrocinador_carga(client, superadmin):
    response = client.get("/patrocinador/")
    assert response.status_code == 200
    assert b"patrocinador" in response.data.lower() 


def test_humo_consulta_basica_patrocinador(client, superadmin):
    resp = client.post("/patrocinador/", data={"consultar": "1"})
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)

#pytest -W ignore tests/humo/test_patrocinador_humo.py
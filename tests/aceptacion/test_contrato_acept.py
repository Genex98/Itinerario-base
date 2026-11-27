from app.model.contrato_model import ContratoModel


def test_aceptacion_contrato(client, superadmin):
    # 1. Registrar
    resp_reg = client.post(
        "/contratos/",
        data={
            "registrar": "1",
            "id_patrocinador": "1",
            "fecha_inicio": "2026-01-01",
            "fecha_fin": "2026-12-31",
            "tipo": "1",
            "monto_total": "2500.00",
            "estatus": "Borrador",
        },
    )
    assert resp_reg.status_code == 200
    assert "registrado correctamente" in resp_reg.get_json().get("mensaje", "").lower()

    # 2. Consultar
    resp_con = client.post("/contratos/", data={"consultar": "1"})
    assert resp_con.status_code == 200
    lista = resp_con.get_json()
    assert len(lista) > 0
    id_c = lista[-1]["id_contrato"]

    # 3. Editar
    resp_edit = client.post(
        "/contratos/",
        data={
            "editar": str(id_c),
            "id_patrocinador": "1",
            "fecha_inicio": "2026-01-01",
            "fecha_fin": "2026-12-31",
            "tipo": "2",
            "monto_total": "4000.00",
            "estatus": "Vigente",
        },
    )
    assert resp_edit.status_code == 200
    assert "actualizado correctamente" in resp_edit.get_json().get("mensaje", "").lower()

    # 4. Eliminar
    resp_del = client.post("/contratos/", data={"eliminar": str(id_c)})
    assert resp_del.status_code == 200
    assert "eliminado correctamente" in resp_del.get_json().get("mensaje", "").lower()
    assert ContratoModel().obtener_por_id(id_c)["estado"] == '0'

#pytest -W ignore tests/aceptacion/test_contrato_acept.py
#pytest -W ignore tests/aceptacion/test_contrato_acept.py -v -s -o addopts=""
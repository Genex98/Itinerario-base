from app.model.patrocinador_model import PatrocinadorModel


def test_aceptacion_patrocinador(client, superadmin):

    # 1. Registrar
    resp_reg = client.post(
        "/patrocinador/",
        data={
            "registrar": "1",
            "nombre_empresa": "Patrocinador Aceptacion CA",
            "rif": "J-123456789",
            "tipo_contrato": "1",
            "nombre_contacto": "Ana Torres",
            "telefono": "04145556677",
            "email": "ana@aceptacion.com",
            "encargado_id": superadmin.id,
        },
    )
    assert resp_reg.status_code == 200
    assert "registrado correctamente" in resp_reg.get_json().get("mensaje", "").lower()

    # 2. Consultar
    resp_con = client.post("/patrocinador/", data={"consultar": "1"})
    assert resp_con.status_code == 200
    creado = next((p for p in resp_con.get_json() if p.get("rif") == "J-123456789"), None)
    assert creado is not None
    id_p = creado["id_patrocinador"]

    # 3. Editar
    resp_edit = client.post(
        "/patrocinador/",
        data={
            "editar": str(id_p),
            "nombre_empresa": "Patrocinador Editado CA",
            "rif": "J-123456789",
            "tipo_contrato": "2",
            "nombre_contacto": "Ana Torres",
            "telefono": "04145556677",
            "email": "ana@aceptacion.com",
            "encargado_id": superadmin.id,
        },
    )
    assert resp_edit.status_code == 200
    assert "actualizado correctamente" in resp_edit.get_json().get("mensaje", "").lower()


    # 4. Eliminar
    resp_del = client.post("/patrocinador/", data={"eliminar": str(id_p)})
    assert resp_del.status_code == 200
    assert "eliminado correctamente" in resp_del.get_json().get("mensaje", "").lower()
    assert PatrocinadorModel().obtener_por_id(id_p)["estado"] == 0


# pytest -W ignore tests/aceptacion/test_patrocinante_acept.py
# pytest -W ignore tests/aceptacion/test_patrocinante_acept.py -v -s -o addopts=""
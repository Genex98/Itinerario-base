import pytest
from app.model.contrato_model import ContratoModel
from app.model.patrocinador_model import PatrocinadorModel


def patrocinador_ejemplo(encargado_id, nombre="Patrocinador Contrato Base CA", rif="J-121212121"):
    """Helper interno para crear un patrocinador válido antes de registrar un contrato."""
    p_model = PatrocinadorModel()
    p_model.set_nombre_empresa(nombre)
    p_model.set_rif(rif)
    p_model.set_tipo_contrato("1")
    p_model.set_nombre_contacto("Contacto Contrato")
    p_model.set_telefono("04141112233")
    p_model.set_email("contratos@prueba.com")
    p_model.set_encargado_id(encargado_id)
    assert p_model.confirmar_registro() is True
    for p in p_model.consultar(activos=True):
        if p["rif"] == rif:
            return p["id_patrocinador"]
    raise AssertionError("No se encontró el patrocinador base creado")

def contrato_prueba(encargado_id, id_patrocinador=None, monto="1500.00", estatus="Vigente", rif_base="J-121212121"):
    """Helper interno para insertar un contrato válido en la BD de prueba."""
    if id_patrocinador is None:
        id_patrocinador = patrocinador_ejemplo(encargado_id, rif=rif_base)

    modelo = ContratoModel()
    modelo.set_id_patrocinador(id_patrocinador)
    modelo.set_fecha_inicio("2026-01-01")
    modelo.set_fecha_fin("2026-12-31")
    modelo.set_tipo("1")
    modelo.set_monto_total(monto)
    modelo.set_estatus(estatus)
    assert modelo.confirmar_registro() is True

    contrato = modelo.obtener_por_id(modelo._id_contrato)
    assert contrato is not None
    return contrato

def test_api_consultar_contratos_sin_login(client):
    """Bloquea o redirige cuando no hay sesión iniciada."""
    response = client.post("/contratos/", data={"consultar": "1"})
    assert response.status_code in [302, 401, 403]

def test_api_consultar_contratos_autenticado(client, superadmin):
    """Devuelve lista JSON con los campos esperados al consultar."""
    contrato_prueba(superadmin.id, rif_base="J-131313131")

    response = client.post("/contratos/", data={"consultar": "1"})
    assert response.status_code == 200

    datos = response.get_json()
    assert isinstance(datos, list)
    assert len(datos) >= 1
    assert {
        "id_contrato",
        "nombre_empresa",
        "fecha_inicio",
        "fecha_fin",
        "tipo",
        "monto_total",
        "estatus",
    }.issubset(datos[0].keys())

def test_api_buscar_contrato_existente(client, superadmin):
    """Busca contrato por ID existente """
    creado = contrato_prueba(superadmin.id, monto="2500.50", rif_base="J-141414141")

    resp_ok = client.post(
        "/contratos/",
        data={"buscar": "1", "id_contrato": creado["id_contrato"]},
    )
    assert resp_ok.status_code == 200
    body_ok = resp_ok.get_json()
    assert body_ok["status"] is True
    assert body_ok["datos"]["id_contrato"] == creado["id_contrato"]
    assert float(body_ok["datos"]["monto_total"]) == 2500.50

def test_api_buscar_contrato_inexistente(client, superadmin):
    """Busca contrato por  ID inexistente."""
    creado = contrato_prueba(superadmin.id, monto="2500.50", rif_base="J-141414141")

    resp_ok = client.post(
        "/contratos/",
        data={"buscar": "1", "id_contrato": creado["id_contrato"]},
    )
    resp_no = client.post("/contratos/", data={"buscar": "1", "id_contrato": 999999})
    assert resp_no.status_code == 200
    assert resp_no.get_json() == {"status": False, "datos": None}

def test_api_registrar_contrato_monto_negativo(client, superadmin):

    id_pat = patrocinador_ejemplo(superadmin.id, rif="J-202020202")

    response = client.post(
        "/contratos/",
        data={
            "registrar": "1",
            "id_patrocinador": id_pat,
            "fecha_inicio": "2026-01-01",
            "fecha_fin": "2026-12-31",
            "tipo": "1",
            "monto_total": "-150.00",
            "estatus": "Borrador",
        },
    )

    assert response.status_code in [200, 400]
    body = response.get_json()
    if response.status_code == 200:
        assert body.get("mensaje") != "Contrato registrado correctamente"
    else:
        assert "error" in body

def test_api_registrar_contrato_exitoso_200(client, superadmin):
    """Registra un contrato válido vía POST y verifica la respuesta exitosa 200."""
    id_pat = patrocinador_ejemplo(superadmin.id, rif="J-191919191")

    response = client.post(
        "/contratos/",
        data={
            "registrar": "1",
            "id_patrocinador": id_pat,
            "fecha_inicio": "2026-03-01",
            "fecha_fin": "2026-12-31",
            "tipo": "1",
            "monto_total": "2200.00",
            "estatus": "Borrador",
        },
    )
    assert response.status_code == 200
    assert response.get_json().get("mensaje") == "Contrato registrado correctamente"

    contratos = ContratoModel().consultar(activos=True)
    assert any(c["id_patrocinador"] == id_pat and float(c["monto_total"]) == 2200.00 for c in contratos)

def test_api_registrar_contrato_error_validacion_400(client, superadmin):
    """Retorna 400 si se envía un tipo o estatus inválido en el registro."""
    id_pat = patrocinador_ejemplo(superadmin.id, rif="J-151515151")

    response = client.post(
        "/contratos/",
        data={
            "registrar": "1",
            "id_patrocinador": id_pat,
            "fecha_inicio": "2026-01-01",
            "fecha_fin": "2026-12-31",
            "tipo": "99",
            "monto_total": "1000",
            "estatus": "Borrador",
        },
    )
    assert response.status_code == 400
    assert "error" in response.get_json()

def test_api_registrar_contrato_sin_permiso_403(client, crear_usuario, login, monkeypatch):
    """Retorna 403 cuando el usuario no tiene el permiso contrato.create."""
    usuario = crear_usuario(rol="Operador")
    login(usuario)

    monkeypatch.setattr(type(usuario), "tiene_permiso", lambda self, permiso: False)

    response = client.post(
        "/contratos/",
        data={
            "registrar": "1",
            "id_patrocinador": 1,
            "fecha_inicio": "2026-01-01",
            "fecha_fin": "2026-12-31",
            "tipo": "1",
            "monto_total": "1000",
            "estatus": "Borrador",
        },
    )
    assert response.status_code == 403
    assert response.get_json()["error"] == "No tienes permiso para esta accion"

def test_api_editar_contrato(client, superadmin):
    """Prueba la edición de un contrato existente desde el endpoint."""
    creado = contrato_prueba(superadmin.id, monto="1200.00", estatus="Borrador", rif_base="J-161616161")
    id_c = creado["id_contrato"]

    resp_edit = client.post(
        "/contratos/",
        data={
            "editar": str(id_c),
            "id_patrocinador": creado["id_patrocinador"],
            "fecha_inicio": "2026-02-01",
            "fecha_fin": "2026-11-30",
            "tipo": "2",
            "monto_total": "3000.00",
            "estatus": "Vigente",
        },
    )
    assert resp_edit.status_code == 200
    assert "actualizado correctamente" in resp_edit.get_json().get("mensaje", "")

def test_api_eliminar_contrato(client, superadmin):
    """Prueba la eliminación lógica de un contrato desde el endpoint."""
    creado = contrato_prueba(superadmin.id, monto="800.00", estatus="Vigente", rif_base="J-171717171")
    id_c = creado["id_contrato"]

    resp_del = client.post("/contratos/", data={"eliminar": str(id_c)})
    assert resp_del.status_code == 200
    assert "eliminado correctamente" in resp_del.get_json().get("mensaje", "")

    activos = ContratoModel().consultar(activos=True)
    assert all(c["id_contrato"] != id_c for c in activos)

def test_api_obtener_contrato_por_id_json_200(client, superadmin):
    """Prueba GET /contratos/api/obtener/<id> para contrato existente."""
    creado = contrato_prueba(superadmin.id, monto="4500.00", estatus="Vigente", rif_base="J-181818181")
    id_c = creado["id_contrato"]

    resp_200 = client.get(f"/contratos/api/obtener/{id_c}")
    assert resp_200.status_code == 200
    data_200 = resp_200.get_json()
    assert data_200["id_contrato"] == id_c
    assert data_200["estatus"] == "Vigente"
    assert float(data_200["monto_total"]) == 4500.00

def test_api_obtener_contrato_por_id_json_404(client, superadmin):
    
    """Prueba GET /contratos/api/obtener/<id> cuando no existe el contrato."""
    resp_404 = client.get("/contratos/api/obtener/999999")
    assert resp_404.status_code == 404
    assert resp_404.get_json() == {"error": "No encontrado"}

#pytest -W ignore tests/backend/test_contrato_backend.py

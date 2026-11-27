import pytest
from app.model.patrocinador_model import PatrocinadorModel


def patrocinador_prueba(encargado_id, nombre="Patrocinador Base CA", rif="J-222222223"):
    """Helper interno para insertar un patrocinador válido en la BD de prueba."""
    modelo = PatrocinadorModel()
    modelo.set_nombre_empresa(nombre)
    modelo.set_rif(rif)
    modelo.set_tipo_contrato("1")
    modelo.set_nombre_contacto("Contacto Prueba")
    modelo.set_telefono("04145551122")
    modelo.set_email("contacto@prueba.com")
    modelo.set_encargado_id(encargado_id)
    assert modelo.confirmar_registro() is True
    for p in modelo.consultar(activos=True):
        if p["rif"] == rif:
            return p
    raise AssertionError("No se encontró el patrocinador recién creado")

def test_api_consultar_patrocinadores_autenticado(client, superadmin):
    """Devuelve lista JSON con los campos esperados al consultar."""
    patrocinador_prueba(superadmin.id, nombre="Patrocinador Consulta CA", rif="J-303030301")

    response = client.post("/patrocinador/", data={"consultar": "1"})
    assert response.status_code == 200

    datos = response.get_json()
    assert isinstance(datos, list)
    assert len(datos) >= 1
    assert {
        "id_patrocinador",
        "nombre_empresa",
        "rif",
        "tipo_contrato",
        "nombre_contacto",
        "telefono",
        "email",
        "encargado_id",
        "encargado_nombre",
    }.issubset(datos[0].keys())

def test_api_consultar_patrocinadores_sin_login(client):
    """Bloquea o redirige cuando no hay sesión iniciada."""
    response = client.post("/patrocinador/", data={"consultar": "1"})
    assert response.status_code in [302, 401, 403]

def test_api_verificar_empresa_existente(client, superadmin):

    patrocinador_prueba(superadmin.id, nombre="Empresa Unica CA", rif="J-404040402")

    resp_existe = client.post("/patrocinador/", data={"verificar_nombre": "Empresa Unica CA"})
    assert resp_existe.status_code == 200
    assert resp_existe.get_json() == {"existe": True}

def test_api_verificar_empresa_inexistente(client, superadmin):
   
    resp_no_existe = client.post("/patrocinador/", data={"verificar_nombre": "Empresa Que No Existe 999"})
    assert resp_no_existe.status_code == 200
    assert resp_no_existe.get_json() == {"existe": False}

def test_api_registrar_patrocinador_error_validacion_400(client, superadmin):
    response = client.post(
        "/patrocinador/",
        data={
            "registrar": "1",
            "nombre_empresa": "Empresa Inválida CA",
            "rif": "J-606060604",
            "tipo_contrato": "99",
            "encargado_id": superadmin.id,
        },
    )
    assert response.status_code == 400
    assert "error" in response.get_json()

def test_api_registrar_sin_permiso_403(client, crear_usuario, login, monkeypatch):
    usuario = crear_usuario(rol="Operador")
    login(usuario)

    monkeypatch.setattr(type(usuario), "tiene_permiso", lambda self, permiso: False)

    response = client.post(
        "/patrocinador/",
        data={
            "registrar": "1",

            "nombre_empresa": "Sin Permiso CA",
            "rif": "J-707070705",
            "tipo_contrato": "1",
            "encargado_id": usuario.id,
        },
    )
    assert response.status_code == 403
    assert response.get_json()["error"] == "No tienes permiso para esta accion"

def test_api_editar_patrocinador(client, superadmin):

    creado = patrocinador_prueba(superadmin.id, nombre="Empresa Original CA", rif="J-808080806")
    id_p = creado["id_patrocinador"]

    # Editar
    resp_edit = client.post(
        "/patrocinador/",
        data={
            "editar": str(id_p),
            "nombre_empresa": "Empresa Editada CA",
            "rif": "J-808080806",
            "tipo_contrato": "2",
            "nombre_contacto": "Nuevo Contacto",
            "telefono": "04120001122",
            "email": "editado@prueba.com",
            "encargado_id": superadmin.id,
        },
    )
    assert resp_edit.status_code == 200
    assert "actualizado correctamente" in resp_edit.get_json().get("mensaje", "")

def test_api_eliminar_patrocinador(client, superadmin):
    """Prueba el flujo de eliminación lógica desde el endpoint."""
    creado = patrocinador_prueba(superadmin.id, nombre="Empresa Original CA", rif="J-808080807")
    id_p = creado["id_patrocinador"]

  
    # Eliminar (borrado lógico)
    resp_del = client.post("/patrocinador/", data={"eliminar": str(id_p)})
    assert resp_del.status_code == 200
    assert "eliminado correctamente" in resp_del.get_json().get("mensaje", "")

    # Verificar que ya no aparece en activos
    activos = PatrocinadorModel().consultar(activos=True)
    assert all(p["id_patrocinador"] != id_p for p in activos)

def test_api_obtener_por_id_json_200(client, superadmin):
    """Prueba GET api/obtener <id> para registro existente"""
    creado = patrocinador_prueba(superadmin.id, nombre="Empresa API GET CA", rif="J-909090907")
    id_p = creado["id_patrocinador"]

    resp_200 = client.get(f"/patrocinador/api/obtener/{id_p}")
    assert resp_200.status_code == 200
    data_200 = resp_200.get_json()
    assert data_200["id_patrocinador"] == id_p
    assert data_200["nombre_empresa"] == "Empresa API GET CA"

def test_api_obtener_por_id_json_404(client, superadmin):

    """Prueba GET api/obtener <id> para registro 404."""
    resp_404 = client.get("/patrocinador/api/obtener/999999")
    assert resp_404.status_code == 404
    assert resp_404.get_json() == {"error": "No encontrado"}

  #pytest -W ignore tests/backend/test_patrocinador_backend.py

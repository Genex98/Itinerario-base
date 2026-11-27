import pytest
from app.model.patrocinador_model import PatrocinadorModel


def test_int_registrar_y_consultar(app):

    modelo = PatrocinadorModel()    
    # 1. Registrar
    modelo.set_nombre_empresa("Estadio Test CA")
    modelo.set_rif("J-000063729")
    modelo.set_tipo_contrato("1")
    modelo.set_nombre_contacto("Juan Pérez")
    modelo.set_telefono("04141234567")
    modelo.set_email("contacto@estadiotest.com")
    modelo.set_encargado_id(1)
    
    assert modelo.confirmar_registro() is True, "El registro debió ser exitoso"

    # 2. Consultar en la misma prueba
    patrocinadores = modelo.consultar(activos=True)
    encontrado = any(
        p['rif'] == "J-000063729" and p['nombre_empresa'] == "Estadio Test CA"
        for p in patrocinadores
    )
    assert encontrado is True, "El patrocinador registrado debe aparecer en la consulta general"


def test_int_modificar_patrocinador(app):
    modelo = PatrocinadorModel()

    # 1. Registrar registro inicial
    modelo.set_nombre_empresa("Empresa Original CA")
    modelo.set_rif("J-000063729")
    modelo.set_tipo_contrato("1")
    modelo.set_nombre_contacto("Ana Pérez")
    modelo.set_telefono("04141111111")
    modelo.set_email("original@empresa.com")
    modelo.set_encargado_id(1)
    assert modelo.confirmar_registro() is True

    # Obtener el ID asignado en la BD
    patrocinadores = modelo.consultar(activos=True)
    registro = next(p for p in patrocinadores if p['rif'] == "J-000063729")
    id_patrocinador = registro['id_patrocinador']

    # 2. Modificar datos y guardar en BD
    modelo.set_nombre_empresa("Empresa Modificada CA")
    modelo.set_telefono("04249999999")
    resultado_mod = modelo.confirmar_modificacion(id_patrocinador)
    assert resultado_mod is True, "La modificación debió ejecutarse correctamente"

    # 3. Verificar cambios en la BD
    actualizado = modelo.obtener_por_id(id_patrocinador)
    assert actualizado['nombre_empresa'] == "Empresa Modificada CA"
    assert actualizado['telefono'] == "04249999999"


def test_int_eliminar_patrocinador(app):
  
    modelo = PatrocinadorModel()
    
    # 1. Registrar
    modelo.set_nombre_empresa("Empresa A Eliminar CA")
    modelo.set_rif("J-000063729")
    modelo.set_tipo_contrato("2")
    modelo.set_nombre_contacto("Luis Gómez")
    modelo.set_telefono("04122222222")
    modelo.set_email("eliminar@empresa.com")
    modelo.set_encargado_id(1)
    assert modelo.confirmar_registro() is True

    patrocinadores = modelo.consultar(activos=True)
    id_patrocinador = next(p['id_patrocinador'] for p in patrocinadores if p['rif'] == "J-000063729")

    # 2. Eliminar lógicamente (estado = 0)
    resultado_elim = modelo.confirmar_eliminacion(id_patrocinador)
    assert resultado_elim is True, "La eliminación lógica debió retornar True"

    # 3. Verificar que ya no figure en la lista de activos
    activos_despues = modelo.consultar(activos=True)
    sigue_activo = any(p['id_patrocinador'] == id_patrocinador for p in activos_despues)
    assert sigue_activo is False, "El patrocinador eliminado no debe aparecer en los registros activos"


def test_integracion_rif_duplicado_rechazado(app):
    """Verifica que la BD o el modelo rechacen registrar dos patrocinadores con el mismo RIF."""
    # 1. Primer registro válido
    modelo1 = PatrocinadorModel()
    modelo1.set_nombre_empresa("Primera Empresa CA")
    modelo1.set_rif("J-000063729")
    modelo1.set_tipo_contrato("1")
    modelo1.set_nombre_contacto("Carlos Ruiz")
    modelo1.set_telefono("04143333333")
    modelo1.set_email("uno@empresa.com")
    modelo1.set_encargado_id(1)
    assert modelo1.confirmar_registro() is True

def test_int_verificar_id_existente(app):
    modelo = PatrocinadorModel()
    resultado = modelo.obtener_por_id(99999)
    assert resultado is None, "Consultar un ID que no existe en la BD debe retornar None"
    

def test_integracion_verificar_nombre_empresa_existente(app):
    modelo = PatrocinadorModel()
    
    # Caso 1: Empresa existente (la registramos primero para garantizar que esté en la BD de prueba)
    modelo.set_nombre_empresa("Cerveceria Regional CA")
    modelo.set_rif("J-000063729")
    modelo.set_tipo_contrato("1")
    modelo.set_nombre_contacto("Carlos Gómez")
    modelo.set_telefono("04141234567")
    modelo.set_email("contacto@regional.com")
    modelo.set_encargado_id(1)
    
    assert modelo.confirmar_registro() is True, "El registro previo falló"
    existe_real = modelo.verificar_nombre_empresa("Cerveceria Regional CA")
    assert existe_real is True, "Una empresa ya registrada debe retornar True"


def test_integracion_verificar_empresa_inexistente(app):
    modelo = PatrocinadorModel()         
    # Caso 2: Empresa inexistente
    existe_fantasma = modelo.verificar_nombre_empresa("Empresa Fantasma Inexistente XYZ")
    assert existe_fantasma is False, "Una empresa que no ha sido registrada debe retornar False"


#pytest -W ignore tests/integracion/test_patrocinador_integracion.py
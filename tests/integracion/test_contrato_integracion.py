import pytest
from app.model.patrocinador_model import PatrocinadorModel
from app.model.contrato_model import ContratoModel

@pytest.fixture
def patrocinador_auxiliar(app):

    p_model = PatrocinadorModel()
    p_model.set_nombre_empresa("Empresa Contrato S.A.")
    p_model.set_rif("J-555555550")
    p_model.set_tipo_contrato("1")
    p_model.set_nombre_contacto("Gerente Test")
    p_model.set_telefono("04129999999")
    p_model.set_email("contrato@empresa.com")
    p_model.set_encargado_id(1)
    p_model.confirmar_registro()
    
    # Consultamos para obtener el ID asignado
    lista = p_model.consultar(activos=True)
    for p in lista:
        if p['rif'] == "J-555555550":
            return p['id_patrocinador']
    return 1

def test_integracion_registrar_y_consultar_contrato(app, patrocinador_auxiliar):
    modelo = ContratoModel()
    
    # Asignar datos válidos para el contrato
    modelo.set_id_patrocinador(patrocinador_auxiliar)
    modelo.set_fecha_inicio("2026-01-01")
    modelo.set_fecha_fin("2026-12-31")
    modelo.set_tipo("1")
    modelo.set_monto_total(1500.00)
    modelo.set_estatus("Vigente")
    
    # Ejecutar el registro
    resultado = modelo.confirmar_registro()
    assert resultado is True, "El registro del contrato debió ser exitoso en la BD de prueba"
    
    # Consultar la lista de contratos activos
    contratos = modelo.consultar(activos=True)
    assert len(contratos) > 0, "Debería haber al menos un contrato registrado en la base de datos"

    # Verificar que el contrato recién creado aparezca y traiga el nombre de la empresa asociada (gracias al JOIN)
    encontrado = False
    for c in contratos:
        if c['id_patrocinador'] == patrocinador_auxiliar:
            encontrado = True
            assert c['estatus'] == "Vigente"
            assert float(c['monto_total']) == 1500.00
            assert c['nombre_empresa'] == "Empresa Contrato S.A."
            break
        
    assert encontrado is True, "El contrato registrado debe aparecer en la consulta general con su respectiva empresa"

def test_integracion_modificar_contrato(app, patrocinador_auxiliar):

    modelo = ContratoModel()    
    # 1. Registrar contrato inicial
    modelo.set_id_patrocinador(patrocinador_auxiliar)
    modelo.set_fecha_inicio("2026-02-01")
    modelo.set_fecha_fin("2026-08-01")
    modelo.set_tipo("2")
    modelo.set_monto_total(800.00)
    modelo.set_estatus("Borrador")
    assert modelo.confirmar_registro() is True
    
    id_contrato = modelo._id_contrato
    assert id_contrato is not None, "El modelo debió guardar el lastrowid tras registrar"

    # 2. Modificar datos y guardar en BD
    modelo.set_monto_total(2250.50)
    modelo.set_estatus("Vigente")
    resultado_mod = modelo.confirmar_modificacion(id_contrato)
    assert resultado_mod is True, "La modificación del contrato debió retornar True"

    # 3. Consultar por ID y verificar persistencia
    actualizado = modelo.obtener_por_id(id_contrato)
    assert actualizado is not None
    assert actualizado['estatus'] == "Vigente"
    assert float(actualizado['monto_total']) == 2250.50

def test_integracion_eliminar_contrato(app, patrocinador_auxiliar):

    modelo = ContratoModel()    
    # 1. Registrar contrato
    modelo.set_id_patrocinador(patrocinador_auxiliar)
    modelo.set_fecha_inicio("2026-03-01")
    modelo.set_fecha_fin("2026-09-01")
    modelo.set_tipo("3")
    modelo.set_monto_total(500.00)
    modelo.set_estatus("Vigente")
    assert modelo.confirmar_registro() is True
    
    id_contrato = modelo._id_contrato

    # 2. Eliminar lógicamente (estado = 0)
    resultado_elim = modelo.confirmar_eliminacion(id_contrato)
    assert resultado_elim is True, "La eliminación lógica debió retornar True"

    # 3. Comprobar que no aparezca en la consulta de contratos activos
    activos = modelo.consultar(activos=True)
    sigue_activo = any(c['id_contrato'] == id_contrato for c in activos)
    assert sigue_activo is False, "El contrato eliminado no debe aparecer en los registros activos"

def test_integracion_obtener_contrato_inexistente(app):
    modelo = ContratoModel()
    
    resultado = modelo.obtener_por_id(99999)
    assert resultado is None, "Consultar un ID inexistente debe retornar None"

#pytest -W ignore tests/integracion/test_contrato_integracion.py
#pytest -W ignore tests/integracion/test_contrato_integracion.py  -v -s -o addopts="" 
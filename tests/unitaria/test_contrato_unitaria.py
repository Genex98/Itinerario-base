import pytest
from app.model.contrato_model import ContratoModel


def test_tipo_contrato_valido():

    modelo = ContratoModel()
    
    # Valores válidos no deben arrojar excepciones
    modelo.set_tipo('1')
    assert modelo._tipo == '1'
    
    modelo.set_tipo('2')
    assert modelo._tipo == '2'
    
    modelo.set_tipo('3')
    assert modelo._tipo == '3'

def test_tipo_contrato_invalido():

    modelo = ContratoModel()
    # Valor inválido (lanza ValueError)
    with pytest.raises(ValueError, match="Tipo de contrato inválido"):
        modelo.set_tipo('5')

def test_tipo_contrato2_texto():
    modelo = ContratoModel()
    
    # Valores válidos no deben arrojar excepciones
    modelo.set_tipo('1')
    modelo.set_tipo('2')
    modelo.set_tipo('3')
    
    # Valor inválido (lanza ValueError)
    with pytest.raises(ValueError, match="Tipo de contrato inválido"):
        modelo.set_tipo('Uno')

def test_estatus_valido():

    modelo = ContratoModel()    
    
    # Estatus válidos permitidos
    modelo.set_estatus('Vigente')
    assert modelo._estatus == 'Vigente'

    modelo.set_estatus('Vencido')
    assert modelo._estatus == 'Vencido'

    modelo.set_estatus('Borrador')
    assert modelo._estatus == 'Borrador'
    
def test_estatus_invalido1():

    modelo = ContratoModel()    
 
    # Estatus inválido debe lanzar ValueError
    with pytest.raises(ValueError, match="Estatus inválido"):
        modelo.set_estatus('Cancelado')

def test_estatus_invalido2():

    modelo = ContratoModel()    
 
    # Estatus inválido debe lanzar ValueError
    with pytest.raises(ValueError, match="Estatus inválido"):
        modelo.set_estatus('123456789')        

def test_estatus_numerico():

    modelo = ContratoModel()    
    
    # Estatus válidos permitidos
    modelo.set_estatus('Vigente')
    modelo.set_estatus('Vencido')
    modelo.set_estatus('Borrador')
    
    # Estatus inválido debe lanzar ValueError
    with pytest.raises(ValueError, match="Estatus inválido"):
        modelo.set_estatus('11111')

def test_validar_fechas1_contrato_incoherentes():

    modelo = ContratoModel()
    modelo.set_id_patrocinador(1)
    modelo.set_tipo('1')

    #CASO 1
    # Fecha de inicio posterior a la fecha de fin
    modelo.set_fecha_inicio('2026-12-31')
    modelo.set_fecha_fin('2026-01-01')
    
    #debe retornar False y registrar el error correspondiente
    assert modelo._validar_datos_contrato() is False
    assert 'La fecha de fin no puede ser anterior a la fecha de inicio' in modelo.errores

def test_validar_fechas2_invalidas():

    modelo = ContratoModel()
    modelo.set_id_patrocinador(1)
    modelo.set_tipo('1')

    
    #Caso 2 Fecha de fin inválida
    modelo.set_fecha_inicio('2026-01-01')
    modelo.set_fecha_fin('2026-02-30')  # 30 de febrero no existe
    assert modelo._validar_datos_contrato() is False
    assert len(modelo.errores) > 0

def test_fecha3_texto():
    
    modelo = ContratoModel()
    modelo.set_id_patrocinador(1)
    modelo.set_tipo('1')

    
     # Caso 3: Formato de fecha con texto
    modelo.set_fecha_inicio('fecha-invalida')
    modelo.set_fecha_fin('2026-12-31')
    assert modelo._validar_datos_contrato() is False
    assert len(modelo.errores) > 0

def test_validar_monto_1_valido():

    modelo = ContratoModel()
    modelo.set_id_patrocinador(1)
    modelo.set_tipo('1')
    modelo.set_fecha_inicio('2026-01-01')
    modelo.set_fecha_fin('2026-12-31')
    
    # Monto Positivo
    modelo.set_monto_total(150)
    assert modelo._validar_datos_contrato() is True   

def test_validar_monto_2_En0():

    modelo = ContratoModel()
    modelo.set_id_patrocinador(1)
    modelo.set_tipo('1')
    modelo.set_fecha_inicio('2026-01-01')
    modelo.set_fecha_fin('2026-12-31')
    
    # Monto cero
    modelo.set_monto_total(0)
    assert modelo._validar_datos_contrato() is False
    assert 'El monto debe ser mayor a 0' in modelo.errores

def test_validar_monto_3_Negativo():

    modelo = ContratoModel()
    modelo.set_id_patrocinador(1)
    modelo.set_tipo('1')
    modelo.set_fecha_inicio('2026-01-01')
    modelo.set_fecha_fin('2026-12-31')
    
    # Monto cero o negativo
    modelo.set_monto_total(-50.00)
    assert modelo._validar_datos_contrato() is False
    assert 'El monto debe ser mayor a 0' in modelo.errores


 #pytest tests/unitaria/test_contrato_unitaria.py
#pytest -W ignore tests/unitaria/test_contrato_unitaria.py

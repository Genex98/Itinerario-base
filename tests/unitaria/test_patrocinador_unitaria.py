import pytest
from app.model.patrocinador_model import PatrocinadorModel

def test_tipo_contrato_valido():
    """Verifica que se acepten los tipos de contrato válidos ('1', '2', '3')."""
    modelo = PatrocinadorModel()
    
    # Asignar un tipo de contrato válido no debe lanzar excepciones
    modelo.set_tipo_contrato('1')
    modelo.set_tipo_contrato('2')
    modelo.set_tipo_contrato('3')

def test_tipo_contrato_invalido():
    """Verifica que se lance un ValueError si el tipo de contrato no es válido."""
    modelo = PatrocinadorModel()
    
    with pytest.raises(ValueError, match="Tipo de contrato inválido"):
        modelo.set_tipo_contrato('99')

def test_encargado_id_Valido():
    """Verifica que se lance un ValueError si el encargado ID tiene un formato incorrecto."""
    modelo = PatrocinadorModel()
# Caso válido: No debe lanzar excepción
    modelo.set_encargado_id("1")
    modelo.set_encargado_id(25)

def test_encargado_id_invalido():
# Casos inválidos: Deben lanzar ValueError
    modelo = PatrocinadorModel()

     # Casos inválido 1: Numero negativo 
    with pytest.raises(ValueError, match="Encargado inválido"):
        modelo.set_encargado_id("-5")    
    # Casos inválidos 2: Texto 
    with pytest.raises(ValueError, match="Encargado inválido"):
        modelo.set_encargado_id("abc_no_valido")

def test_validar_rif_correcto():
    modelo = PatrocinadorModel()
   
    modelo.set_nombre_empresa("Empresa Test")
    modelo.set_tipo_contrato("1")
    modelo.set_encargado_id("1")
    modelo.set_rif("INVALIDO")  # Formato incorrecto de RIF
    modelo.set_email("contacto@empresa.com")
    
     # Casos de RIF VALIDO
    modelo.set_rif("G-200000007")
    assert modelo._validar_datos_patrocinador() is True

    # RIF persona natural válido
    modelo.set_rif("V-123456780")
    assert modelo._validar_datos_patrocinador() is True

def test_validar_rif_incorrecto():
    modelo = PatrocinadorModel()
       
    modelo.set_nombre_empresa("Empresa Test")
    modelo.set_tipo_contrato("1")
    modelo.set_encargado_id("1")
    modelo.set_email("contacto@empresa.com")


    # Caso de RIF erróneo
    modelo.set_rif("INVALIDO")  # Formato incorrecto de RIF       
    assert modelo._validar_datos_patrocinador() is False
    # Caso de RIF Mal formato
    modelo.set_rif("V-1234567-0")  # Formato incorrecto de RIF       
    assert modelo._validar_datos_patrocinador() is False 

def test_formato_email_valido():
    """Verifica que se rechacen correos electrónicos con formato incorrecto o vacíos."""
    modelo = PatrocinadorModel()
    modelo.set_rif("J-000063729")
    modelo.set_nombre_empresa("Empresa Valida CA")
    modelo.set_tipo_contrato("1")
    modelo.set_encargado_id("1")

    # Caso 1: Correo sin arroba
    modelo.set_email("MAIZORITOS@MAIZORITOS.com")
    assert modelo._validar_datos_patrocinador() is True
    
def test_formato_email_invalido():
    """Verifica que se rechacen correos electrónicos con formato incorrecto o vacíos."""
    modelo = PatrocinadorModel()
    modelo.set_rif("J-000063729")
    modelo.set_nombre_empresa("Empresa Valida CA")
    modelo.set_tipo_contrato("1")
    modelo.set_encargado_id("1")

    # Caso 1: Correo sin arroba
    modelo.set_email("correo_sin_arroba.com")
    assert modelo._validar_datos_patrocinador() is False

    # Caso 2: Correo sin dominio
    modelo.set_email("contacto@")
    assert modelo._validar_datos_patrocinador() is False

    # Caso 3: Correo sin punto
    modelo.set_email("correo_con_arroba@sinpunto")
    assert modelo._validar_datos_patrocinador() is False

def test_longitud_nombre_empresa1_corto():

    modelo = PatrocinadorModel()
    modelo.set_rif("J-000063729")
    modelo.set_tipo_contrato("1")
    modelo.set_encargado_id("1")
    modelo.set_email("polar@polar.com")
    
    # Caso 1: Nombre muy corto 
    modelo.set_nombre_empresa("A")
    assert modelo._validar_datos_patrocinador() is False  

def test_longitud_nombre_empresa2_Valido():

    modelo = PatrocinadorModel()
    modelo.set_rif("J-000063729")
    modelo.set_tipo_contrato("1")
    modelo.set_encargado_id("1")
    modelo.set_email("Tunal@tunal.com")
    
 # Caso 2: Nombre dentro del rango válido    
    modelo.set_nombre_empresa("Empresa Valida CA")
    assert modelo._validar_datos_patrocinador() is True

def test_longitud_nombre_empresa3_Max():

    modelo = PatrocinadorModel()
    modelo.set_rif("J-000063729")
    modelo.set_tipo_contrato("1")
    modelo.set_encargado_id("1")
    modelo.set_email("Nestea@Nestea.com")
    
    # Caso 3: Nombre excede el límite máximo
    modelo.set_nombre_empresa("N" * 256)
    assert modelo._validar_datos_patrocinador() is False

def test_modelo_vacio_y_espacios_en_blanco():

    # Caso 1: Instancia recién creada sin atributos asignados
    modelo_vacio = PatrocinadorModel()
    assert modelo_vacio._validar_datos_patrocinador() is False

    # Caso 2: Nombre por espacios en blanco
    modelo_espacios = PatrocinadorModel()
    modelo_espacios.set_rif("J-000063729")
    modelo_espacios.set_tipo_contrato("1")
    modelo_espacios.set_encargado_id("1")
    modelo_espacios.set_email("contacto@empresa.com")
    modelo_espacios.set_nombre_empresa("     ")
    assert modelo_espacios._validar_datos_patrocinador() is False
    
#pytest -W ignore tests/unitaria/test_patrocinador_unitaria.py
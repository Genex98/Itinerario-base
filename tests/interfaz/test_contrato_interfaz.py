import os
from playwright.sync_api import Page, expect

BASE_URL = os.getenv("APP_BASE_URL", "http://127.0.0.1:5001")


def test_ui_contrato_carga(page: Page):
    page.goto(f"{BASE_URL}/contratos/", wait_until="domcontentloaded")

    # 1. Carga sin errores visibles
    expect(page.locator("body")).to_be_visible()
    expect(page.locator("body")).not_to_contain_text("Internal Server Error")
    expect(page.locator("body")).not_to_contain_text("Traceback")

def test_ui_contrato_elementos(page: Page):
    page.goto(f"{BASE_URL}/contratos/", wait_until="domcontentloaded")

    # 2. Revisar elementos visibles en pantalla (ejemplo con tabla o encabezado)
    expect(page.locator("table, h1, h2").first).to_be_visible()


def test_ui_contrato_resultado_accion(page: Page):
    page.goto(f"{BASE_URL}/contratos/", wait_until="domcontentloaded")
    
    # 3. Comprobar resultado en la UI tras una acción (ejemplo: clic en botón o filtro)
    boton_consultar = page.locator("button:has-text('Consultar'), input[type='submit']").first
    if boton_consultar.count() > 0:
        boton_consultar.click()
        expect(page.locator("body")).not_to_contain_text("Internal Server Error")
        expect(page.locator("body")).to_be_visible()

    #pytest -W ignore tests/interfaz/test_contrato_interfaz.py

    #pytest -W ignore tests/interfaz/test_contrato_interfaz.py  -v -s -o addopts="" 

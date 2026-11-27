"""Pruebas end-to-end del flujo público de acceso a Itinerario.

El CAPTCHA no es una imagen: los cuatro caracteres están en el DOM dentro de
`.captcha-tile`, así que se leen desde la página y se escriben en el formulario.
No se desactiva nada en el servidor.
"""
import os
import re

import pytest
from playwright.sync_api import Page, expect


def leer_captcha(page: Page) -> str:
    tiles = page.locator(".captcha-tile")
    expect(tiles).to_have_count(4)
    return "".join(texto.strip() for texto in tiles.all_text_contents())


def captcha_incorrecto(codigo: str) -> str:
    return ("Y" if codigo[0] == "Z" else "Z") + codigo[1:]


def test_raiz_redirige_al_login(page: Page):
    page.goto("/")
    expect(page).to_have_url(re.compile(r"/auth/login$"))
    expect(
        page.get_by_role("heading", name=re.compile(r"Iniciar\s+Sesi[oó]n", re.I))
    ).to_be_visible()


def test_formulario_muestra_campos(page: Page):
    page.goto("/auth/login")
    expect(page.locator("#email")).to_be_visible()
    expect(page.locator("#password")).to_be_visible()
    expect(page.locator("#captcha_text")).to_be_visible()
    expect(page.locator("#btnLogin")).to_be_visible()


def test_captcha_tiene_cuatro_caracteres(page: Page):
    page.goto("/auth/login")
    assert re.fullmatch(r"[A-Z0-9]{4}", leer_captcha(page))


def test_refrescar_captcha_cambia_codigo(page: Page):
    page.goto("/auth/login")
    anterior = leer_captcha(page)

    for _ in range(5):
        with page.expect_response("**/auth/refresh-captcha"):
            page.locator(".captcha-refresh").click()
        page.wait_for_timeout(200)
        if leer_captcha(page) != anterior:
            return

    pytest.fail("El CAPTCHA no cambió después de refrescarlo")


def test_captcha_incompleto_se_marca_en_el_cliente(page: Page):
    page.goto("/auth/login")
    page.fill("#email", "demo@example.com")
    page.fill("#password", "Abcd1234")
    page.fill("#captcha_text", "AB")
    page.click("#btnLogin")

    expect(page.locator("#captcha_text")).to_have_class(re.compile(r"is-invalid"))
    expect(page).to_have_url(re.compile(r"/auth/login$"))


def test_servidor_rechaza_captcha_incorrecto(page: Page):
    page.goto("/auth/login")
    real = leer_captcha(page)

    page.fill("#email", "demo@example.com")
    page.fill("#password", "Abcd1234")
    page.fill("#captcha_text", captcha_incorrecto(real))
    page.click("#btnLogin")

    expect(page.locator("#captcha_text")).to_have_class(re.compile(r"is-invalid"))
    expect(page.locator(".captcha-input-row .invalid-feedback")).to_have_text(
        re.compile(r"Codigo incorrecto", re.I)
    )


def test_pantalla_recuperar_password_carga(page: Page):
    page.goto("/auth/forgot-password")
    expect(
        page.get_by_role("heading", name=re.compile(r"Recuperar\s+Contrase[ñn]a", re.I))
    ).to_be_visible()
    expect(page.locator('input[name="email"]')).to_be_visible()
    expect(page.locator("#captcha_text")).to_be_visible()
    expect(page.locator("#btnSend")).to_be_visible()


EMAIL = os.environ.get("E2E_EMAIL")
PASSWORD = os.environ.get("E2E_PASSWORD")


@pytest.mark.skipif(
    not (EMAIL and PASSWORD),
    reason="Definir E2E_EMAIL y E2E_PASSWORD para ejecutar el login real",
)
def test_login_con_credenciales_llega_al_dashboard(page: Page):
    page.goto("/auth/login")
    page.fill("#email", EMAIL)
    page.fill("#password", PASSWORD)
    page.fill("#captcha_text", leer_captcha(page))
    page.click("#btnLogin")

    page.wait_for_url(re.compile(r"/dashboard"), timeout=30_000)

"""Preparación común de las pruebas end-to-end.

Antes de la primera prueba se levanta el servidor Flask con el Python del venv
del proyecto y se espera a que /auth/login responda. Al terminar se apaga.
"""
import os
import subprocess
import time
import urllib.request

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON = os.path.join(RAIZ, "venv", "bin", "python")
PUERTO = int(os.environ.get("E2E_PORT", "5001"))
BASE_URL = os.environ.get("E2E_BASE_URL", f"http://127.0.0.1:{PUERTO}")
LOGIN = f"{BASE_URL}/auth/login"

COMANDO = [
    PYTHON,
    "-c",
    (
        "from app import create_app, socketio; "
        "socketio.run(create_app(), host='127.0.0.1', "
        f"port={PUERTO}, debug=False, use_reloader=False, "
        "allow_unsafe_werkzeug=True)"
    ),
]


def _responde(url: str, timeout: float = 1.0) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout):
            return True
    except Exception:
        return False


def _esperar(url: str, limite: float = 120.0) -> None:
    inicio = time.time()
    while time.time() - inicio < limite:
        if _responde(url):
            return
        time.sleep(0.5)
    raise RuntimeError(f"El servidor no respondió en {limite:.0f} s: {url}")


@pytest.fixture(scope="session", autouse=True)
def servidor():
    # Si ya hay un servidor encendido en el puerto, se reutiliza.
    if _responde(LOGIN):
        yield BASE_URL
        return

    proceso = subprocess.Popen(
        COMANDO,
        cwd=RAIZ,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    try:
        _esperar(LOGIN)
        yield BASE_URL
    finally:
        proceso.terminate()
        try:
            proceso.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proceso.kill()

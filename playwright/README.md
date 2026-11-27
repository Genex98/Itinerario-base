# Pruebas end-to-end con Playwright y pytest

Pruebas del sistema Itinerario en un navegador real. La carpeta es independiente
de la aplicación: no se modifica nada de `app/`, `run.py` ni de la suite de
pruebas de backend que vive en `tests/`.

## Requisitos

- Python del proyecto (`venv/`).
- MySQL encendido y el archivo `.env` configurado en la raíz.
- El servidor Flask no hay que levantarlo a mano: `conftest.py` lo arranca y lo
  apaga alrededor de la ejecución.

## Instalación

```bash
source venv/bin/activate        # desde la raíz del proyecto
pip install -r playwright/requirements.txt
python -m playwright install chromium
```

## Ejecución

```bash
cd playwright
../venv/bin/pytest              # suite completa
../venv/bin/pytest --headed     # con el navegador visible
../venv/bin/pytest -k captcha   # solo los casos de CAPTCHA
../venv/bin/pytest --browser firefox
```

El reporte HTML queda en `reporte.html` y los artefactos de los fallos en
`test-results/`.

## Estructura

```
playwright/
├── pytest.ini          # configuración de pytest y de Playwright
├── conftest.py         # levanta el servidor Flask
├── requirements.txt
└── tests/
    └── test_login.py   # flujo público de acceso
```

## Qué se prueba

- La raíz redirige al login.
- El formulario muestra sus cuatro controles.
- El CAPTCHA se genera con cuatro caracteres y cambia al refrescarse.
- Un CAPTCHA incompleto se bloquea en el cliente.
- Un CAPTCHA incorrecto se rechaza en el servidor.
- La pantalla de recuperación de contraseña carga.
- El login con credenciales llega al dashboard (opcional).

## Sobre el CAPTCHA

Los cuatro caracteres están en el DOM dentro de `.captcha-tile`. Las pruebas los
leen desde la página y los escriben en el formulario, sin desactivar el CAPTCHA
ni tocar el backend. La validación real la sigue haciendo el servidor.

## Evidencia ante fallos

Con `--tracing`, `--video` y `--screenshot` en `retain-on-failure`, cada prueba
que falla deja en `test-results/` una captura, un video y un `trace.zip`:

```bash
../venv/bin/playwright show-trace test-results/<carpeta>/trace.zip
```

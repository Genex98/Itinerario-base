# [Equipo N°] - Itinerario (gestión operativa del estadio) - Playwright

> Antes de publicar: reemplazar **[Equipo N°]**, **[Sección]** y el enlace del repositorio.

## Resumen ejecutivo

Este trabajo documenta la implementación de pruebas automatizadas end-to-end con Playwright sobre
Itinerario, un sistema web de gestión operativa construido con Flask y MySQL. El alcance se concentró en
el flujo público de acceso: redirección de la raíz al login, renderizado del formulario, generación y
refresco del CAPTCHA, validación en el cliente, rechazo del CAPTCHA en el servidor y carga de la pantalla
de recuperación de contraseña. La suite quedó formada por ocho casos: siete se ejecutan sin credenciales y
uno se activa opcionalmente mediante variables de entorno. La configuración levanta el servidor Flask
automáticamente, reutiliza el Python del entorno virtual y conserva trace, captura y video únicamente
cuando una prueba falla. En la ejecución final se obtuvieron siete pruebas aprobadas, una omitida y un
tiempo total de 9,9 segundos. Además se provocó un fallo controlado para analizar los artefactos de
diagnóstico, y se documentó el proceso completo de instalación, configuración, ejecución e interpretación
de resultados.

## Adjunto 1: guía de instalación y uso

**`guia.pdf`** (22 páginas). Contiene:

- Requisitos y verificación del entorno Python.
- Instalación paso a paso de `pytest-playwright`, `pytest-html` y Chromium.
- Explicación de `pytest.ini` y de la fixture que levanta Flask (`conftest.py`).
- Cómo están escritas las pruebas, incluido el manejo del CAPTCHA sin desactivarlo en el servidor.
- Comandos de uso diario y modos de ejecución.
- Resultados reales de la corrida: 7 aprobadas, 1 omitida y 0 fallidas en 9,9 segundos.
- Análisis de un fallo controlado con captura, video y Trace Viewer.
- Dificultades encontradas, limitaciones y trabajo futuro.

## Adjunto 2: diapositivas y repositorio

- **`diapositivas.pptx`** (12 láminas editables): problema, herramienta, arquitectura, instalación,
  configuración, resultados y aprendizajes.
- **Repositorio:** `[enlace al repositorio]`, carpeta **`playwright/`**.

```
playwright/
├── pytest.ini          # configuración de pytest y Playwright
├── conftest.py         # levanta el servidor Flask
├── requirements.txt    # pytest-playwright y pytest-html
├── tests/test_login.py
├── evidencias/         # capturas, video y trace de la corrida
├── guia.pdf
└── diapositivas.pptx
```

## Evidencias de la ejecución

| Métrica | Resultado |
| --- | --- |
| Casos detectados | 8 |
| Aprobados | 7 |
| Omitidos | 1 (login con credenciales) |
| Fallidos | 0 |
| Tiempo total | 9,9 s (pytest en serie) |

El detalle de cada caso, las duraciones y las capturas están en la guía y en `playwright/evidencias/`.

## Cómo reproducirlo

```bash
pip install -r playwright/requirements.txt
python -m playwright install chromium
cd playwright
../venv/bin/pytest
```

Requisitos: Python del proyecto, MySQL encendido y el archivo `.env` con `SECRET_KEY`.

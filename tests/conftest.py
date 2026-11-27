import os
import re
import sys
import uuid
from pathlib import Path

import pymysql
import pytest
from pymysql.constants import CLIENT
from pymysql.cursors import DictCursor

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# nombre original -> nombre de prueba (solo esquemas clonados)
TEST_DBS = {'estadio_db': 'estadio_db_test', 'seguridad': 'seguridad_test'}

# Hay consultas de la app que escriben el esquema "seguridad." de forma
# explícita (JOIN seguridad.usuarios...). En tests se reescriben para que
# apunten a seguridad_test y nunca lean la BD real.
RE_ESQUEMA = re.compile(r'(?<![A-Za-z0-9])(?:)?(estadio_db|seguridad)(?:`)?\.')


def _redirigir_esquemas(sql):
    if not sql or not isinstance(sql, str):
        return sql
    return RE_ESQUEMA.sub(lambda m: f'{m.group(1)}_test.', sql)


class _DictCursorTest(DictCursor):
    """Cursor que redirige cualquier referencia a los esquemas reales."""

    def execute(self, query, args=None):
        return super().execute(_redirigir_esquemas(query), args)

    def executemany(self, query, args):
        return super().executemany(_redirigir_esquemas(query), args)

# dumps de respaldo si el .sql de la raíz viene vacío
DUMPS_RESERVA = {
    'estadio_db.sql': ROOT / 'Docss' / 'estadio_db.sql',
    'seguridad.sql': ROOT / 'Docss' / 'seguridad.sql',
}


def _creds():
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'charset': 'utf8mb4',
    }


def _ruta_dump(archivo):
    ruta = ROOT / archivo
    if ruta.exists() and ruta.stat().st_size > 100:
        return ruta
    return DUMPS_RESERVA[archivo]


def _aplicar_dump(conn, archivo):
    """Aplica un .sql de la raíz sobre la BD de prueba.

    Los dumps traen CREATE DATABASE / USE con los nombres reales; se renombra
    únicamente esos tokens backtick-eados para redirigir todo al *_test.
    """
    sql = _ruta_dump(archivo).read_text(encoding='utf-8')
    sql = re.sub(r'(estadio_db|seguridad)', r'\1_test', sql)
    with conn.cursor() as cur:
        cur.execute(sql)  # requiere MULTI_STATEMENTS en la conexión
        while cur.nextset():
            pass


@pytest.fixture(scope='session', autouse=True)
def bases_de_prueba():
    from dotenv import load_dotenv
    load_dotenv(ROOT / '.env')
    conn = pymysql.connect(client_flag=CLIENT.MULTI_STATEMENTS, **_creds())
    try:
        with conn.cursor() as cur:
            for test in TEST_DBS.values():
                cur.execute(f'DROP DATABASE IF EXISTS {test}')
                cur.execute(f'CREATE DATABASE {test} DEFAULT CHARACTER SET utf8mb4')
        _aplicar_dump(conn, 'estadio_db.sql')
        _aplicar_dump(conn, 'seguridad.sql')
    finally:
        conn.close()
    yield


@pytest.fixture()
def app(monkeypatch):
    # apunta la config a las BDs de prueba ANTES de crear la app.
    # monkeypatch.setitem restaura la config real al terminar cada test.
    from app import config
    for origen, test in TEST_DBS.items():
        monkeypatch.setitem(config.DATABASE_CONFIG[origen], 'database', test)
        # permite Database.get_connection('estadio_db_test') además del
        # nombre lógico 'estadio_db'; ambas conexiones caen en la BD de prueba.
        monkeypatch.setitem(
            config.DATABASE_CONFIG, test, {**config.DATABASE_CONFIG[origen], 'database': test}
        )
    monkeypatch.setenv('SECRET_KEY', 'clave-de-test')

    # redirige también las consultas que nombran el esquema de forma explícita
    import app.database as database
    monkeypatch.setattr(database, 'DictCursor', _DictCursorTest)

    # nunca enviar correos reales
    from app.helpers import email_service
    from app.controller import auth_controller
    monkeypatch.setattr(email_service, 'enviar_email_recuperacion', lambda *a, **k: True)
    monkeypatch.setattr(auth_controller, 'enviar_email_recuperacion', lambda *a, **k: True)

    from app import create_app
    application = create_app()
    application.config['TESTING'] = True
    application.config['WTF_CSRF_ENABLED'] = False

    # verificación dura: cada conexión debe estar en su BD *_test
    with application.app_context():
        for origen, test in TEST_DBS.items():
            with database.Database.get_connection(origen).cursor() as cur:
                cur.execute('SELECT DATABASE() AS db')
                actual = cur.fetchone()['db']
            assert actual == test, f'{origen} apunta a {actual}, se esperaba {test}'

    yield application


@pytest.fixture(autouse=True)
def _contexto(app):
    """Empuja un app context para que las llamadas directas a modelos tengan flask.g."""
    with app.app_context():
        yield


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def crear_usuario(app):
    """Crea usuarios directamente en seguridad_test."""
    def _crear(rol='Superadmin', activo=True, password='Clave1234'):
        from werkzeug.security import generate_password_hash
        from app.model.auth_model import UsuarioModel
        email = f'test_{uuid.uuid4().hex[:8]}@prueba.com'
        usuario = UsuarioModel().registrar({
            'nombre': 'Usuario Prueba',
            'email': email,
            'password_hash': generate_password_hash(password),
            'cedula': uuid.uuid4().hex[:10],
            'rol': rol,
        })
        assert usuario is not None, 'No se pudo registrar el usuario de prueba'
        if not activo:
            UsuarioModel().modificar(usuario.id, {'activo': 0})
            usuario = UsuarioModel().obtener_por_id(usuario.id)
        usuario._password = password
        return usuario
    return _crear


@pytest.fixture()
def login(client):
    """Login completo respetando CAPTCHA. Devuelve la respuesta del POST."""
    def _login(usuario, next_page=None, captcha='ABCD'):
        with client.session_transaction() as s:
            s['captcha_code'] = captcha
        url = '/auth/login'
        if next_page:
            url += f'?next={next_page}'
        return client.post(url, data={
            'email': usuario.email,
            'password': getattr(usuario, '_password', ''),
            'captcha_text': captcha,
        })
    return _login


@pytest.fixture()
def superadmin(client, crear_usuario, login):
    """Cliente con sesión iniciada como Superadmin."""
    usuario = crear_usuario(rol='Superadmin')
    login(usuario)
    return usuario
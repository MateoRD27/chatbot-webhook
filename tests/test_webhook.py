import json
import pytest
from app import create_app
from config import Config

# configuracion aislada para no afectar el entorno real
class TestConfig(Config):
    # activacion del modo seguro
    TESTING = True
    DEBUG = True
    # url valida para que el analizador de redis no falle
    REDIS_URL = "redis://localhost:6379/0"
    # memoria volatil para el limitador de ataques
    RATELIMIT_STORAGE_URI = "memory://"

@pytest.fixture
def client():
    # inicializa el servidor web temporalmente
    app = create_app(TestConfig)
    with app.test_client() as client:
        yield client

def test_diagnostico_de_salud(client):
    # verifica la respuesta del balanceador
    response = client.get('/health')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['status'] == 'ok'

def test_bloqueo_de_seguridad_sin_token(client):
    # simula un ataque sin token autorizado
    payload = {"queryResult": {"queryText": "Prueba interna"}}
    response = client.post(
        '/webhook',
        data=json.dumps(payload),
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Token": "llave_falsa"
        }
    )
    
    assert response.status_code == 401
    assert b"acceso no autorizado" in response.data

def test_proteccion_contra_formatos_toxicos(client):
    # inyecta texto plano para forzar un error
    response = client.post(
        '/webhook',
        data="Texto malicioso sin formato",
        headers={
            "Content-Type": "text/plain",
            "X-Webhook-Token": "mi_token_super_secreto"
        }
    )
    
    assert response.status_code == 400
    assert b"se requiere formato json" in response.data
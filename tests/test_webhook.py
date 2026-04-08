import json
import pytest
import requests
from unittest.mock import patch, MagicMock
from app import create_app
from config import Config

# configuracion aislada para no afectar el entorno real
class TestConfig(Config):
    TESTING = True
    DEBUG = True
    REDIS_URL = "redis://localhost:6379/0"
    RATELIMIT_STORAGE_URI = "memory://"
    AZURE_AI_ENDPOINT = "http://endpoint-simulado.com"
    WEBHOOK_SECRET_TOKEN = "Mi_token_secreto"

@pytest.fixture(autouse=True)
def mock_redis():
    # intercepta llamadas a redis exclusivas del health check
    with patch('redis.from_url') as mock_redis_from_url:
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_redis_from_url.return_value = mock_client
        yield mock_client

@pytest.fixture(autouse=True)
def mock_azure():
    # intercepta las llamadas http hacia el microservicio
    with patch('app.clients.azure_ai_client.requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "ok": True,
            "response": "Respuesta generada por el mock de ia"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        yield mock_post

@pytest.fixture
def client():
    # inicializa el servidor web temporalmente
    app = create_app(TestConfig)
    with app.test_client() as client:
        yield client

def test_diagnostico_de_salud(client):
    response = client.get('/health')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['status'] == 'ok'

def test_metodo_http_no_permitido(client):
    # verifica que el webhook rechace peticiones get gracias al nuevo handler 405
    response = client.get('/webhook')
    assert response.status_code == 405

def test_bloqueo_de_seguridad_token_falso(client):
    payload = {"queryResult": {"queryText": "Prueba interna"}}
    response = client.post(
        '/webhook',
        data=json.dumps(payload),
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Token": "Llave_falsa"
        }
    )
    assert response.status_code == 401
    assert b"acceso no autorizado" in response.data

def test_bloqueo_de_seguridad_token_ausente(client):
    payload = {"queryResult": {"queryText": "Prueba sin header"}}
    response = client.post(
        '/webhook',
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 401
    assert b"acceso no autorizado" in response.data

def test_proteccion_contra_formatos_toxicos(client):
    response = client.post(
        '/webhook',
        data="Texto toxico",
        headers={
            "Content-Type": "text/plain",
            "X-Webhook-Token": "Mi_token_secreto"
        }
    )
    assert response.status_code == 400
    assert b"se requiere formato json" in response.data

def test_proteccion_contra_payload_gigante(client):
    payload_gigante = "x" * (3 * 1024 * 1024)
    response = client.post(
        '/webhook',
        data=payload_gigante,
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Token": "Mi_token_secreto"
        }
    )
    assert response.status_code == 413
    assert b"payload demasiado grande" in response.data

def test_ruta_inexistente(client):
    response = client.get('/ruta-fantasma')
    assert response.status_code == 404
    assert b"ruta no encontrada" in response.data

def test_payload_vacio_o_incompleto(client):
    response = client.post(
        '/webhook',
        data=json.dumps({}),
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Token": "Mi_token_secreto"
        }
    )
    assert response.status_code == 200
    assert b"error de enrutamiento" in response.data

def test_json_valido_sin_queryresult(client):
    payload = {"session": "Sesion_incompleta"}
    response = client.post(
        '/webhook',
        data=json.dumps(payload),
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Token": "Mi_token_secreto"
        }
    )
    assert response.status_code == 200
    assert b"error de enrutamiento" in response.data

def test_anomalia_de_enrutamiento(client):
    payload = {
        "session": "Sesion_test",
        "queryResult": {
            "queryText": "Hola",
            "action": "Saludo_simple",
            "intent": {"displayName": "Saludo"}
        }
    }
    response = client.post(
        '/webhook',
        data=json.dumps(payload),
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Token": "Mi_token_secreto"
        }
    )
    assert response.status_code == 200
    assert b"error de enrutamiento" in response.data

def test_flujo_exitoso_rag(client):
    payload = {
        "session": "Sesion_test",
        "queryResult": {
            "queryText": "Fecha de matricula",
            "action": "requiere_rag",
            "intent": {"displayName": "Consulta_fechas"}
        }
    }
    response = client.post(
        '/webhook',
        data=json.dumps(payload),
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Token": "Mi_token_secreto"
        }
    )
    assert response.status_code == 200
    assert b"fulfillmentText" in response.data

def test_flujo_intencion_desconocida(client):
    payload = {
        "session": "Sesion_test",
        "queryResult": {
            "queryText": "Que es el universo",
            "action": "Input.unknown",
            "intent": {"displayName": "Default Fallback Intent"}
        }
    }
    response = client.post(
        '/webhook',
        data=json.dumps(payload),
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Token": "Mi_token_secreto"
        }
    )
    assert response.status_code == 200
    assert b"fulfillmentText" in response.data

def test_falla_microservicio_ia_timeout(client):
    with patch('app.clients.azure_ai_client.requests.post') as mock_post:
        mock_post.side_effect = requests.exceptions.RequestException("Timeout de red")
        
        payload = {
            "session": "Sesion_test",
            "queryResult": {
                "queryText": "Ayuda",
                "action": "requiere_rag",
                "intent": {"displayName": "Consulta"}
            }
        }
        response = client.post(
            '/webhook',
            data=json.dumps(payload),
            headers={
                "Content-Type": "application/json",
                "X-Webhook-Token": "Mi_token_secreto"
            }
        )
        assert response.status_code == 200
        assert b"tuvimos un problema procesando tu mensaje" in response.data

def test_falla_microservicio_ia_respuesta_corrupta(client):
    with patch('app.clients.azure_ai_client.requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.json.side_effect = json.JSONDecodeError("Error", "", 0)
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        payload = {
            "session": "Sesion_test",
            "queryResult": {
                "queryText": "Ayuda",
                "action": "requiere_rag",
                "intent": {"displayName": "Consulta"}
            }
        }
        response = client.post(
            '/webhook',
            data=json.dumps(payload),
            headers={
                "Content-Type": "application/json",
                "X-Webhook-Token": "Mi_token_secreto"
            }
        )
        assert response.status_code == 200
        assert b"tuvimos un problema procesando tu mensaje" in response.data

def test_falla_interna_del_servidor(client):
    # el mock ahora se inyecta donde se usa, para que el try-except local lo atrape
    with patch('app.routes.webhook_routes.process_dialogflow_request') as mock_process:
        mock_process.side_effect = Exception("Falla catastrofica de negocio")
        
        payload = {"queryResult": {"queryText": "Rompe el bot"}}
        response = client.post(
            '/webhook',
            data=json.dumps(payload),
            headers={
                "Content-Type": "application/json",
                "X-Webhook-Token": "Mi_token_secreto"
            }
        )
        # verifica que la app sobrevive devolviendo el fallback local de la ruta
        assert response.status_code == 200
        assert b"tuvimos un problema procesando tu mensaje" in response.data

def test_defensa_ddos_limite_tasa(client):
    payload = json.dumps({"queryResult": {"queryText": "Spam"}})
    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Token": "Mi_token_secreto"
    }
    for _ in range(60):
        client.post('/webhook', data=payload, headers=headers)
        
    response = client.post('/webhook', data=payload, headers=headers)
    assert response.status_code == 429
    assert b"demasiadas peticiones" in response.data
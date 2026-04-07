import json
import pytest
from app import create_app
from config import Config

# configuracion aislada para no afectar el entorno real
class TestConfig(Config):
    TESTING = True
    DEBUG = True
    REDIS_URL = "redis://localhost:6379/0"
    RATELIMIT_STORAGE_URI = "memory://"

@pytest.fixture
def client():
    # inicializa el servidor temporalmente
    app = create_app(TestConfig)
    with app.test_client() as client:
        yield client

def test_diagnostico_de_salud(client):
    # verifica la respuesta del balanceador
    response = client.get('/health')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['status'] == 'ok'

def test_bloqueo_de_seguridad_token_falso(client):
    # simula un ataque con credenciales incorrectas
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

def test_bloqueo_de_seguridad_token_ausente(client):
    # simula una peticion publica sin la cabecera de autorizacion
    payload = {"queryResult": {"queryText": "Prueba sin header"}}
    response = client.post(
        '/webhook',
        data=json.dumps(payload),
        headers={
            "Content-Type": "application/json"
        }
    )
    
    assert response.status_code == 401
    assert b"acceso no autorizado" in response.data

def test_proteccion_contra_formatos_toxicos(client):
    # inyecta texto plano para forzar el rechazo
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

def test_proteccion_contra_payload_gigante(client):
    # envia un archivo masivo para probar el escudo ddos
    payload_gigante = "x" * (3 * 1024 * 1024)
    response = client.post(
        '/webhook',
        data=payload_gigante,
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Token": "mi_token_super_secreto"
        }
    )
    
    assert response.status_code == 413
    assert b"payload demasiado grande" in response.data

def test_ruta_inexistente(client):
    # confirma que rutas fantasmas no rompan la app
    response = client.get('/ruta-fantasma')
    
    assert response.status_code == 404
    assert b"ruta no encontrada" in response.data

def test_payload_vacio_o_incompleto(client):
    # simula un fallo critico donde dialogflow no envia datos
    response = client.post(
        '/webhook',
        data=json.dumps({}),
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Token": "mi_token_super_secreto"
        }
    )
    
    # el codigo responde 200 pero notifica la anomalia de enrutamiento
    assert response.status_code == 200
    assert b"error de enrutamiento" in response.data

def test_anomalia_de_enrutamiento(client):
    # simula que dialogflow envia un saludo que no debio llegar aqui
    payload = {
        "session": "sesion_test",
        "queryResult": {
            "queryText": "Hola",
            "action": "saludo_simple",
            "intent": {"displayName": "saludo"}
        }
    }
    response = client.post(
        '/webhook',
        data=json.dumps(payload),
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Token": "mi_token_super_secreto"
        }
    )
    
    assert response.status_code == 200
    assert b"error de enrutamiento" in response.data

def test_flujo_exitoso_rag(client):
    # evalua el camino principal de conocimiento
    payload = {
        "session": "sesion_test",
        "queryResult": {
            "queryText": "Fecha de matricula",
            "action": "requiere_rag",
            "intent": {"displayName": "consulta_fechas"}
        }
    }
    response = client.post(
        '/webhook',
        data=json.dumps(payload),
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Token": "mi_token_super_secreto"
        }
    )
    
    assert response.status_code == 200
    assert b"fulfillmentText" in response.data

def test_flujo_intencion_desconocida(client):
    # evalua que la ia maneje entradas incomprensibles para dialogflow
    payload = {
        "session": "sesion_test",
        "queryResult": {
            "queryText": "Que es el universo",
            "action": "input.unknown",
            "intent": {"displayName": "Default Fallback Intent"}
        }
    }
    response = client.post(
        '/webhook',
        data=json.dumps(payload),
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Token": "mi_token_super_secreto"
        }
    )
    
    assert response.status_code == 200
    assert b"fulfillmentText" in response.data

def test_defensa_ddos_limite_tasa(client):
    # bombardea el servidor para verificar el firewall en memoria
    payload = json.dumps({"queryResult": {"queryText": "Spam"}})
    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Token": "mi_token_super_secreto"
    }
    
    for _ in range(60):
        client.post('/webhook', data=payload, headers=headers)
        
    response = client.post('/webhook', data=payload, headers=headers)
    
    assert response.status_code == 429
    assert b"demasiadas peticiones" in response.data
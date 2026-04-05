import os
from dotenv import load_dotenv

# carga las variables del archivo .env a la memoria
load_dotenv()

class Config:
    SECRET_KEY = os.environ['SECRET_KEY']
    WEBHOOK_SECRET_TOKEN = os.environ['WEBHOOK_SECRET_TOKEN']
    
    DEBUG = os.environ.get('FLASK_DEBUG', default='0') == '1'
    
    AZURE_AI_ENDPOINT = os.environ.get('AZURE_AI_ENDPOINT', 'endpoint_simulado')
    AZURE_AI_KEY = os.environ.get('AZURE_AI_KEY', 'llave_simulada')
    
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # sincronizacion del firewall de peticiones con redis para entornos multi-worker
    RATELIMIT_STORAGE_URI = REDIS_URL
    
    # cadena de conexion para azure application insights (opentelemetry)
    APPLICATIONINSIGHTS_CONNECTION_STRING = os.environ.get('APPLICATIONINSIGHTS_CONNECTION_STRING', '')
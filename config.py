import os
from dotenv import load_dotenv

# carga las variables del archivo .env a la memoria
load_dotenv()

class Config:
    """
    configuracion centralizada de la aplicacion
    """
    # principio fail fast: la app falla si no existen estas credenciales
    SECRET_KEY = os.environ['SECRET_KEY']
    WEBHOOK_SECRET_TOKEN = os.environ['WEBHOOK_SECRET_TOKEN']
    
    DEBUG = os.environ.get('FLASK_DEBUG', default='0') == '1'
    
    # en produccion cambiar .get() por el acceso directo os.environ['VAR']
    AZURE_AI_ENDPOINT = os.environ.get('AZURE_AI_ENDPOINT', 'endpoint_simulado')
    AZURE_AI_KEY = os.environ.get('AZURE_AI_KEY', 'llave_simulada')
    REDIS_URL = os.environ.get('REDIS_URL', 'url_redis_simulada')
# app/routes/webhook_routes.py
from flask import Blueprint, request, jsonify, current_app
import logging
import secrets 
import redis
from redis.exceptions import RedisError
from app.services.dialogflow_service import process_dialogflow_request
from app import limiter

webhook_bp = Blueprint('webhook', __name__)
logger = logging.getLogger(__name__)

# endpoint de monitoreo de infraestructura para el balanceador de azure
@webhook_bp.route('/health', methods=['GET'])
@limiter.exempt # eximimos esta ruta para que los pings de azure no sean bloqueados
def health_check():
    """
    punto de entrada ligero para verificar la salud del microservicio y sus dependencias
    """
    status = {"status": "ok", "redis": "desconectado"}
    try:
        r = redis.from_url(current_app.config.get('REDIS_URL', ''))
        if r.ping():
            status["redis"] = "conectado"
    except RedisError:
        logger.warning("health check detecto falla en conexion a redis")
    
    return jsonify(status), 200

# proteccion ddos: maximo 60 peticiones por minuto (1 por segundo) por cada ip
@webhook_bp.route('/webhook', methods=['POST'])
@limiter.limit("60 per minute") 
def webhook_endpoint():
    """
    punto de entrada que valida seguridad perimetral antes de procesar la logica de negocio
    """
    auth_header = request.headers.get('X-Webhook-Token', '')
    expected_token = current_app.config.get('WEBHOOK_SECRET_TOKEN', '')
    
    if not expected_token or not secrets.compare_digest(auth_header, expected_token):
        logger.warning("rechazo de seguridad: token de acceso invalido o ausente")
        return jsonify({"error": "acceso no autorizado"}), 401

    if request.content_length and request.content_length > 2 * 1024 * 1024:
        logger.warning("rechazo de seguridad: payload entrante supera el limite de 2mb")
        return jsonify({"error": "payload demasiado grande"}), 413

    if not request.is_json:
        logger.warning("rechazo de seguridad: la peticion no contiene formato json")
        return jsonify({"error": "se requiere formato json"}), 400

    payload = request.get_json()

    try:
        response_data = process_dialogflow_request(payload)
        logger.info("peticion orquestada y respondida exitosamente")
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"falla en logica de negocio: {str(e)}", exc_info=True)
        fallback = {
            "fulfillmentText": "tuvimos un problema procesando tu mensaje. intenta de nuevo."
        }
        return jsonify(fallback), 200
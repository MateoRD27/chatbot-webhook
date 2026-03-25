from flask import Blueprint, request, jsonify, current_app
import logging
import secrets 
from app.services.dialogflow_service import process_dialogflow_request

webhook_bp = Blueprint('webhook', __name__)
logger = logging.getLogger(__name__)

@webhook_bp.route('/webhook', methods=['POST'])
def webhook_endpoint():
    """
    punto de entrada que valida seguridad perimetral antes de procesar
    """
    # obtenemos el token entrante y el esperado. usamos strings vacios por defecto para evitar errores tipo nonetype
    auth_header = request.headers.get('X-Webhook-Token', '')
    expected_token = current_app.config.get('WEBHOOK_SECRET_TOKEN', '')
    
    # compare_digest evita que un atacante adivine el token midiendo los milisegundos de respuesta (timing attack)
    if not expected_token or not secrets.compare_digest(auth_header, expected_token):
        logger.warning("rechazo de seguridad: token de acceso invalido o ausente")
        return jsonify({"error": "acceso no autorizado"}), 401

    #  seguridad, prevencion de ataques de saturacion de memoria dos (limite 2mb)
    if request.content_length and request.content_length > 2 * 1024 * 1024:
        logger.warning("rechazo de seguridad: payload entrante supera el limite de 2mb")
        return jsonify({"error": "payload demasiado grande"}), 413

    #  seguridad, verificacion de formato de datos
    if not request.is_json:
        logger.warning("rechazo de seguridad: la peticion no contiene formato json")
        return jsonify({"error": "se requiere formato json"}), 400

    payload = request.get_json()

    try:
        # delegacion a la capa de servicios
        response_data = process_dialogflow_request(payload)
        logger.info("peticion orquestada y respondida exitosamente")
        return jsonify(response_data), 200
        
    except Exception as e:
        # si hay error azure lo rastreara desde aqui hasta su origen
        logger.error(f"falla en logica de negocio: {str(e)}", exc_info=True)
        fallback = {
            "fulfillmentText": "tuvimos un problema procesando tu mensaje. intenta de nuevo."
        }
        return jsonify(fallback), 200
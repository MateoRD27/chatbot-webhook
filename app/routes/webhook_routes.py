from flask import Blueprint, request, jsonify, current_app
import logging
from app.services.dialogflow_service import process_dialogflow_request

webhook_bp = Blueprint('webhook', __name__)
logger = logging.getLogger(__name__)

@webhook_bp.route('/webhook', methods=['POST'])
def webhook_endpoint():
    """
    recibe y valida la peticion de dialogflow
    """
    # seguridad: verificacion del token enviado por dialogflow
    auth_header = request.headers.get('X-Webhook-Token')
    if auth_header != current_app.config['WEBHOOK_SECRET_TOKEN']:
        logger.warning("acceso bloqueado por token ausente o invalido")
        return jsonify({"error": "acceso no autorizado"}), 401

    # validacion de formato
    if not request.is_json:
        logger.warning("peticion rechazada por no ser json")
        return jsonify({"error": "se requiere formato json"}), 400

    payload = request.get_json()

    try:
        # envio a la capa de servicios
        response_data = process_dialogflow_request(payload)
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"error procesando webhook: {str(e)}", exc_info=True)
        fallback = {
            "fulfillmentText": "tuvimos un problema procesando tu mensaje. intenta de nuevo."
        }
        return jsonify(fallback), 200
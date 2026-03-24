# app/routes/webhook_routes.py
from flask import Blueprint, request, jsonify, current_app
import logging
from app.services.dialogflow_service import process_dialogflow_request

webhook_bp = Blueprint('webhook', __name__)
logger = logging.getLogger(__name__)

@webhook_bp.route('/webhook', methods=['POST'])
def webhook_endpoint():
    """
    punto de entrada que valida seguridad perimetral antes de procesar
    """
    # 1. seguridad: validacion estricta del token de dialogflow
    auth_header = request.headers.get('X-Webhook-Token')
    if auth_header != current_app.config['WEBHOOK_SECRET_TOKEN']:
        logger.warning("rechazo de seguridad: token de acceso invalido o ausente")
        return jsonify({"error": "acceso no autorizado"}), 401

    # 2. seguridad: prevencion de ataques de saturacion de memoria (limite 2mb)
    if request.content_length and request.content_length > 2 * 1024 * 1024:
        logger.warning("rechazo de seguridad: payload entrante supera el limite de 2mb")
        return jsonify({"error": "payload demasiado grande"}), 413

    # 3. seguridad: verificacion de formato de datos
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
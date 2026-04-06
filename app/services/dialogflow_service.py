import logging
from typing import Dict, Any
from flask import current_app
from app.clients.azure_ai_client import AzureAIFoundryClient
from app.utils.response_formatter import build_text_response

logger = logging.getLogger(__name__)

def process_dialogflow_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    orquesta el flujo evaluando la accion y delegando la peticion a la ia.
    """
    query_result = payload.get('queryResult', {})
    
    intent_name = query_result.get('intent', {}).get('displayName', 'Fallback_intent').strip()
    action_name = query_result.get('action', 'Sin_accion').strip()
    user_query = query_result.get('queryText', '').strip()
    session_id = payload.get('session', 'Sesion_desconocida').strip()

    logger.info(f"Enrutando sesion: {session_id} | accion: {action_name}")

    # instanciamos el cliente inyectando la url del endpoint de azure
    azure_client = AzureAIFoundryClient(
        endpoint=current_app.config.get('AZURE_AI_ENDPOINT')
    )

    try:
        intent_lower = intent_name.lower()
        
        # validacion estricta de enrutamiento
        if intent_lower == 'default fallback intent' or action_name == 'requiere_rag':
            
            logger.info("Delegando procesamiento al motor rag externo.")
            
            texto_respuesta = azure_client.generate_rag_response(
                user_query=user_query, 
                session_id=session_id
            )
            
            return build_text_response(texto_respuesta)

        else:
            logger.warning(f"Anomalia de enrutamiento: accion '{action_name}' no soportada.")
            return build_text_response("Lo siento, hubo un error de enrutamiento interno. por favor intenta reformular tu pregunta.")

    except Exception as e:
        logger.error(f"Error critico en integracion de ia: {str(e)}")
        raise RuntimeError("Error en el gateway de ia")
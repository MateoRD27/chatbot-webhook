# app/services/dialogflow_service.py
import logging
from typing import Dict, Any
from flask import current_app
from app.clients.azure_ai_client import AzureAIFoundryClient
from app.repositories.session_repository import SessionRepository
from app.utils.response_formatter import build_text_response

logger = logging.getLogger(__name__)

def process_dialogflow_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    orquesta el flujo evaluando la accion, sanitizando datos y delegando a la ia
    """
    query_result = payload.get('queryResult', {})
    
    # extraccion y sanitizacion basica de los textos de entrada
    intent_name = query_result.get('intent', {}).get('displayName', 'fallback_intent').strip()
    action_name = query_result.get('action', 'sin_accion').strip()
    user_query = query_result.get('queryText', '').strip()
    parameters = query_result.get('parameters', {})
    session_id = payload.get('session', 'sesion_desconocida').strip()

    logger.info(f"sesion: {session_id} | accion: {action_name} | intent: {intent_name}")
    logger.debug(f"parametros extraidos de nlu: {parameters}")

    # inyeccion de dependencias
    session_repo = SessionRepository(
        redis_url=current_app.config.get('REDIS_URL', 'mock_redis')
    )
    azure_client = AzureAIFoundryClient(
        endpoint=current_app.config.get('AZURE_AI_ENDPOINT', 'mock_endpoint'),
        api_key=current_app.config.get('AZURE_AI_KEY', 'mock_key')
    )

    try:
        # 1. gestion de memoria de la conversacion
        thread_id = session_repo.get_thread_id(session_id)
        
        if not thread_id:
            logger.info("sesion nueva detectada. aprovisionando thread.")
            thread_id = azure_client.create_new_thread()
            session_repo.save_thread_id(session_id, thread_id)
        else:
            logger.info(f"recuperando contexto del thread: {thread_id}")

        # 2. enrutamiento dinamico basado en el contrato de la accion
        if intent_name == 'Default Fallback Intent' or action_name == 'requiere_rag':
            logger.info("accion requiere_rag validada. consultando motor de ia.")
            texto_respuesta = azure_client.generate_rag_response(
                user_query=user_query, 
                thread_id=thread_id, 
                context_params=parameters
            )
            return build_text_response(texto_respuesta)

        else:
            logger.info("ejecutando procesamiento nativo sin ia.")
            return build_text_response(f"accion procesada de forma segura: {action_name}")

    except Exception as e:
        # elevamos el error para que la capa de rutas y opentelemetry lo registren
        raise RuntimeError(f"error critico en integracion de ia: {str(e)}")
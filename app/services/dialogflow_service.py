import time
import threading
import logging
import redis
from typing import Dict, Any
from flask import current_app
from app.clients.azure_ai_client import AzureAIFoundryClient
from app.utils.response_formatter import build_text_response, build_event_response

logger = logging.getLogger(__name__)

def background_azure_call(app_config: dict, user_query: str, session_id: str):
    """hilo en segundo plano para procesar la ia sin bloquear el reloj de dialogflow."""
    redis_url = app_config.get('REDIS_URL', 'redis://localhost:6379/0')
    try:
        r = redis.from_url(redis_url)
        azure_client = AzureAIFoundryClient(endpoint=app_config.get('AZURE_AI_ENDPOINT'))
        
        # ejecutar llamada pesada
        texto_respuesta = azure_client.generate_rag_response(user_query=user_query, session_id=session_id)
        
        # guardar el resultado en la memoria compartida (redis)
        r.set(f"rag_result:{session_id}", texto_respuesta.encode('utf-8'), ex=600)
        r.set(f"rag_status:{session_id}", b"completed", ex=600)
        logger.info(f"hilo de azure completado con exito para sesion: {session_id}")
        
    except Exception as e:
        logger.error(f"error en hilo de fondo azure para {session_id}: {str(e)}")
        r = redis.from_url(redis_url)
        r.set(f"rag_result:{session_id}", b"Lo siento, el motor de inteligencia tuvo un problema interno.", ex=600)
        r.set(f"rag_status:{session_id}", b"error", ex=600)

def process_dialogflow_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    orquesta el flujo manejando bucles de espera para saltar la restriccion de 5s de dialogflow.
    """
    query_result = payload.get('queryResult', {})
    intent_name = query_result.get('intent', {}).get('displayName', 'Fallback_intent').strip()
    action_name = query_result.get('action', 'Sin_accion').strip()
    user_query = query_result.get('queryText', '').strip()
    session_id = payload.get('session', 'Sesion_desconocida').strip()

    logger.info(f"Enrutando sesion: {session_id} | intent: {intent_name}")

    try:
        intent_lower = intent_name.lower()
        
        # interceptamos peticiones rag (1ra vez) o los eventos de espera 
        if intent_lower == 'default fallback intent' or action_name == 'requiere_rag' or intent_lower == 'intent_espera':
            
            r = redis.from_url(current_app.config.get('REDIS_URL'))
            status_key = f"rag_status:{session_id}"
            result_key = f"rag_result:{session_id}"
            loops_key = f"rag_loops:{session_id}"
            
            status = r.get(status_key)
            
            # fase 1: si no hay estado, es la primera peticion. lanzamos el hilo.
            if status is None:
                logger.info("iniciando procesamiento rag en segundo plano.")
                r.set(status_key, b"processing", ex=600)
                r.set(loops_key, 0, ex=600)
                
                # clonamos la config para el hilo porque sale del contexto de flask
                app_config = current_app.config.copy()
                t = threading.Thread(target=background_azure_call, args=(app_config, user_query, session_id))
                t.start()

            # fase 2: ciclo de espera activo (max 2 segundos para no romper dialogflow)
            max_wait = 2
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                current_status = r.get(status_key)
                
                if current_status in [b"completed", b"error"]:
                    # la ia termino de pensar (puede ser antes de los 15s)
                    final_bytes = r.get(result_key)
                    final_text = final_bytes.decode('utf-8') if final_bytes else "Hubo un problema procesando tu peticion."
                    
                    # limpiamos la memoria y entregamos
                    r.delete(status_key, result_key, loops_key)
                    logger.info("entregando respuesta final a dialogflow.")
                    return build_text_response(final_text)
                
                time.sleep(0.5)
            
            # fase 3: se agotaron los 3.5s y la ia sigue pensando.
            loops = int(r.get(loops_key) or 0)
            loops += 1
            r.set(loops_key, loops, ex=600)

            # si llevamos 4 bucles (15 a 18 segundos aprox), cortamos y avisamos al usuario
            if loops > 10:
                logger.warning(f"timeout rag de bucles (15s) alcanzado para: {session_id}")
                r.delete(status_key, result_key, loops_key)
                return build_text_response("La base de datos está tardando más de lo esperado en procesar la respuesta. Por favor, intenta preguntar de nuevo.")
            
            # relanzar el evento a dialogflow para comprar 5 segundos extra
            logger.info(f"solicitando tiempo a dialogflow (loop de espera {loops})")
            return build_event_response("ESPERA_RAG")

        else:
            logger.warning(f"anomalia de enrutamiento: accion '{action_name}' no soportada.")
            return build_text_response("Lo siento, hubo un error de enrutamiento interno. por favor intenta reformular tu pregunta.")

    except Exception as e:
        logger.error(f"error critico en orquestacion: {str(e)}")
        raise RuntimeError("Error en el gateway de ia")
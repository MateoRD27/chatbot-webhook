import logging
import requests

logger = logging.getLogger(__name__)

class AzureAIFoundryClient:
    """
    cliente rest para comunicarse con el microservicio de inteligencia artificial.
    """
    def __init__(self, endpoint: str):
        self.endpoint = endpoint.rstrip('/')

    def generate_rag_response(self, user_query: str, session_id: str) -> str:
        """
        ejecuta la peticion http delegando el manejo de hilos al agente externo.
        """
        url = f"{self.endpoint}/chat"
        
        payload = {
            "message": user_query,
            "session_id": session_id
        }
        
        logger.info(f"Enviando peticion al agente ia para la sesion: {session_id}")
        
        try:
            # configuramos 115 segundos de timeout para fallar antes que el servidor maestro
            response = requests.post(url, json=payload, timeout=115)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("ok"):
                logger.info("Respuesta exitosa recibida desde la capa de ia.")
                return data.get("response", "Respuesta vacia")
            else:
                error_msg = data.get("error", "Error desconocido en el agente")
                logger.error(f"Falla reportada por el agente: {error_msg}")
                return "Lo siento, el motor de inteligencia tuvo un problema procesando la informacion."
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Caida de red al contactar el microservicio ia: {str(e)}")
            raise RuntimeError("No se pudo establecer comunicacion con el microservicio agente")
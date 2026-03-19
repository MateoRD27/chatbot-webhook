import logging
# import redis  # descomentar para produccion

logger = logging.getLogger(__name__)

class SessionRepository:
    """
    gestiona el mapeo entre la sesion de dialogflow y el thread de azure en redis
    """
    def __init__(self, redis_url: str):
        # self.redis_client = redis.from_url(redis_url) # descomentar para produccion
        
        # diccionario en memoria temporal para simulacion
        self._mock_db = {} 

    def get_thread_id(self, session_id: str) -> str:
        """
        busca el hilo asociado a la sesion del usuario
        """
        # codigo produccion
        # thread_id = self.redis_client.get(session_id)
        # return thread_id.decode('utf-8') if thread_id else none
        
        return self._mock_db.get(session_id)

    def save_thread_id(self, session_id: str, thread_id: str) -> None:
        """
        guarda la sesion con tiempo de expiracion de treinta minutos
        """
        # codigo produccion
        # self.redis_client.setex(session_id, 1800, thread_id)
        
        self._mock_db[session_id] = thread_id
        logger.debug(f"mapeo guardado: sesion {session_id} -> hilo {thread_id}")
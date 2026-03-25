import logging
import redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

class SessionRepository:
    """
    gestiona el mapeo entre la sesion de dialogflow y el thread de azure en redis
    """
    def __init__(self, redis_url: str):
        try:
            self.redis_client = redis.from_url(redis_url)
            # enviamos un ping para validar que el servidor esta vivo al iniciar
            self.redis_client.ping()
        except RedisError as e:
            logger.error(f"falla critica conectando a redis: {str(e)}")
            raise RuntimeError("no se pudo establecer conexion con la base de datos")

    def get_thread_id(self, session_id: str) -> str:
        """
        busca el hilo asociado a la sesion del usuario
        """
        try:
            thread_id = self.redis_client.get(session_id)
            # redis devuelve bytes, asi que lo decodificamos a string
            return thread_id.decode('utf-8') if thread_id else None
        except RedisError as e:
            logger.error(f"error de lectura en redis para sesion {session_id}: {str(e)}")
            return None

    def save_thread_id(self, session_id: str, thread_id: str) -> None:
        """
        guarda la sesion con tiempo de expiracion de treinta minutos (1800 segundos)
        """
        try:
            # setex guarda la llave, el tiempo de vida y el valor previniendo fugas de memoria
            self.redis_client.setex(session_id, 1800, thread_id)
            logger.info(f"memoria persistente guardada en redis: {session_id} -> {thread_id}")
        except RedisError as e:
            logger.error(f"error de escritura en redis para sesion {session_id}: {str(e)}")
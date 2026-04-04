# app/extensions.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Inicializamos el limitador usando la IP del cliente como identificador
limiter = Limiter(key_func=get_remote_address)
import multiprocessing

# configuracion para el servidor wsgi de produccion

bind = "0.0.0.0:5000"

# calcula dinamicamente los workers segun la capacidad de la maquina
workers = multiprocessing.cpu_count() * 2 + 1

# asigna hilos adicionales por worker para peticiones concurrentes ligeras
threads = 2

# si azure ai o redis se demoran mas de 120 segundos, gunicorn mata el proceso
timeout = 120

# observabilidad redirigiendo eventos a la salida estandar 
# esto permite que azure application insights los capture
accesslog = "-"
errorlog = "-"
loglevel = "info"
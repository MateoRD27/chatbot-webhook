# app/__init__.py
import logging
from flask import Flask, jsonify, request
from config import Config
from azure.monitor.opentelemetry import configure_azure_monitor

def create_app(config_class=Config):
    """
    fabrica de la aplicacion con integracion de opentelemetry para azure
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # configuracion estandar de logs. azure monitor interceptara estos logs
    # y los enviara a la nube adjuntando el trace_id automaticamente.
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # inicializacion de telemetria distribuida si hay conexion a azure
    conn_string = app.config.get('APPLICATIONINSIGHTS_CONNECTION_STRING')
    if conn_string:
        try:
            configure_azure_monitor(connection_string=conn_string)
            logging.info("telemetria de azure application insights activada")
        except Exception as e:
            logging.error(f"falla al iniciar telemetria: {str(e)}")

    # middleware de seguridad: registra la ip entrante en la telemetria
    @app.before_request
    def before_request():
        logging.info(f"peticion entrante desde ip: {request.remote_addr}")

    # registro de la capa de rutas
    from app.routes.webhook_routes import webhook_bp
    app.register_blueprint(webhook_bp)

    # manejadores de error globales capturados por la telemetria
    @app.errorhandler(400)
    def bad_request_error(error):
        logging.warning(f"bloqueo por peticion mal formada 400: {error}")
        return jsonify({"error": "peticion incorrecta"}), 400

    @app.errorhandler(404)
    def not_found_error(error):
        logging.warning(f"intento de acceso a ruta inexistente 404: {request.path}")
        return jsonify({"error": "ruta no encontrada"}), 404

    @app.errorhandler(Exception)
    def internal_error(error):
        # opentelemetry enviara la traza completa de este error a tu panel en azure
        logging.error(f"error interno del servidor 500: {str(error)}", exc_info=True)
        fallback = {
            "fulfillmentText": "el sistema esta en mantenimiento. intenta de nuevo mas tarde."
        }
        return jsonify(fallback), 200 

    return app
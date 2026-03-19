from flask import Flask, jsonify
from config import Config
import logging

def create_app(config_class=Config):
    """
    fabrica de la aplicacion flask
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # configuracion de logs para trazabilidad
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # registro de la capa de rutas
    from app.routes.webhook_routes import webhook_bp
    app.register_blueprint(webhook_bp)

    # manejadores de error para que dialogflow siempre reciba json
    @app.errorhandler(400)
    def bad_request_error(error):
        logging.warning(f"peticion mal formada 400: {error}")
        return jsonify({"error": "peticion incorrecta"}), 400

    @app.errorhandler(404)
    def not_found_error(error):
        logging.warning("intento de acceso a ruta inexistente 404")
        return jsonify({"error": "ruta no encontrada"}), 404

    @app.errorhandler(Exception)
    def internal_error(error):
        # captura cualquier error 500 sin detener el servidor
        logging.error(f"error interno 500: {str(error)}", exc_info=True)
        fallback = {
            "fulfillmentText": "el sistema esta en mantenimiento. intenta de nuevo mas tarde."
        }
        return jsonify(fallback), 200 

    return app
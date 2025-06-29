from flask import Flask
from flasgger import Swagger

from app.routes.event_routes import event_bp

def create_app():
    app = Flask(__name__)

    # swagger-docs
    Swagger(app)

    app.register_blueprint(event_bp, url_prefix="/api/events")

    return app

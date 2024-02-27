from flask import Flask

from pulse_backend import api


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(api.bp)
    return app

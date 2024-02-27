from flask import Flask, jsonify


def ping():
    return jsonify({"status": "ok"}), 200


def create_app() -> Flask:
    app = Flask(__name__)
    app.add_url_rule("/api/ping", view_func=ping, methods=["GET"])
    return app

if __name__ == "__main__":
    create_app().run()

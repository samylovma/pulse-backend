from flask import Blueprint, jsonify

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/ping", methods=("GET",))
def ping():
    return jsonify({"status": "ok"}), 200

from flask import g, jsonify, request

from extensions import db
from models import User


PUBLIC_ENDPOINTS = {"home", "health_check", "auth.join"}


def register_auth_middleware(app):
    @app.before_request
    def require_user_id():
        # CORS preflight requests carry no credentials; let flask-cors answer them
        if request.method == "OPTIONS":
            return None
        if request.endpoint is None or request.endpoint in PUBLIC_ENDPOINTS:
            return None

        raw_user_id = request.headers.get("X-User-Id", "").strip()
        if not raw_user_id.isdigit():
            return jsonify({"error": "X-User-Id header is required."}), 400

        user = db.session.get(User, int(raw_user_id))
        if user is None:
            return jsonify({"error": "Unknown user."}), 401

        g.current_user_id = user.id
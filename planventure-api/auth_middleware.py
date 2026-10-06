from flask import g, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request


PUBLIC_ENDPOINTS = {"home", "health_check", "auth.register", "auth.login"}


def register_auth_middleware(app):
    @app.before_request
    def require_access_token():
        # CORS preflight requests carry no credentials; let flask-cors answer them
        if request.method == "OPTIONS":
            return None
        if request.endpoint is None or request.endpoint in PUBLIC_ENDPOINTS:
            return None

        # BTW manually set verify_jwt_in_request()
        verify_jwt_in_request(optional=True)
        g.current_user_id = get_jwt_identity()
from jwt.exceptions import PyJWTError
from flask_jwt_extended import create_access_token, decode_token
from flask_jwt_extended.exceptions import JWTExtendedException


def generate_access_token(identity):
    return create_access_token(identity=str(identity))


def validate_access_token(token):
    try:
        return decode_token(token)
    except (JWTExtendedException, PyJWTError):
        return None
from email_validator import EmailNotValidError, validate_email
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import User


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.post("/register")
def register():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "A JSON request body is required."}), 400

    email = payload.get("email")
    password = payload.get("password")
    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({"error": "Email and password are required."}), 400

    try:
        email = validate_email(
            email.strip(), check_deliverability=False
        ).normalized.lower()
    except EmailNotValidError:
        return jsonify({"error": "A valid email address is required."}), 400

    password_length = len(password.encode("utf-8"))
    if password_length < 8 or password_length > 72:
        return jsonify(
            {"error": "Password must be between 8 and 72 bytes."}
        ), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "An account with that email already exists."}), 409

    user = User(email=email)
    user.set_password(password)
    db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "An account with that email already exists."}), 409

    return jsonify({"id": user.id, "email": user.email}), 201
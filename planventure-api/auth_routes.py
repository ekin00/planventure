import re

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import User


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Names like "GUEST", "GUEST6", "GUEST42" are system-generated for walk-in
# users, so nobody may join with one.
RESERVED_NAME_PATTERN = re.compile(r"^GUEST\d*$")
RESERVED_NAME_MESSAGE = "GUEST names are reserved — pick another name!"


@auth_bp.post("/join")
def join():
    """Find-or-create a user by name. No name -> auto-assign GUEST{id}."""
    payload = request.get_json(silent=True)
    if payload is not None and not isinstance(payload, dict):
        return jsonify({"error": "A JSON request body is required."}), 400

    raw_name = (payload or {}).get("name")
    if raw_name is not None and not isinstance(raw_name, str):
        return jsonify({"error": "name must be a string."}), 400

    name = raw_name.strip().upper() if isinstance(raw_name, str) else ""

    # Reserved-name check happens before any DB lookup, so GUEST names can
    # never be created or joined, whether or not the id exists yet.
    if name and RESERVED_NAME_PATTERN.match(name):
        return jsonify({"error": RESERVED_NAME_MESSAGE}), 400

    if name:
        user = User.query.filter_by(name=name).first()
        if user is not None:
            return jsonify({"id": user.id, "name": user.name}), 200

    user = User(name=name or "PENDING")
    db.session.add(user)
    try:
        db.session.flush()  # assign the id
        if not name:
            user.name = f"GUEST{user.id}"
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        # Lost a race with a concurrent join of the same name.
        user = User.query.filter_by(name=name).first()
        if user is None:
            return jsonify({"error": "Could not create user."}), 500
        return jsonify({"id": user.id, "name": user.name}), 200

    return jsonify({"id": user.id, "name": user.name}), 201
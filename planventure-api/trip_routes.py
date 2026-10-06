from datetime import date

from flask import Blueprint, g, jsonify, request

from extensions import db
from models import Trip


trip_bp = Blueprint("trip", __name__, url_prefix="/trip")


def _trip_to_dict(trip):
    return {
        "id": trip.id,
        "destination": trip.destination,
        "start_date": trip.start_date.isoformat(),
        "end_date": trip.end_date.isoformat(),
        "latitude": trip.latitude,
        "longitude": trip.longitude,
        "itinerary": trip.itinerary,
    }


def _parse_trip_payload(payload, *, partial=False):
    if not isinstance(payload, dict):
        return None, "A JSON request body is required."

    values = {}
    for field in ("destination", "start_date", "end_date"):
        if field not in payload:
            if not partial:
                return None, f"{field} is required."
            continue
        value = payload[field]
        if field == "destination":
            if not isinstance(value, str) or not value.strip():
                return None, "destination must be a non-empty string."
            values[field] = value.strip()
        else:
            if not isinstance(value, str):
                return None, f"{field} must be an ISO-formatted date."
            try:
                values[field] = date.fromisoformat(value)
            except ValueError:
                return None, f"{field} must be an ISO-formatted date."

    for field in ("latitude", "longitude"):
        if field in payload:
            value = payload[field]
            if value is not None and (
                isinstance(value, bool) or not isinstance(value, (int, float))
            ):
                return None, f"{field} must be a number or null."
            values[field] = value

    if "itinerary" in payload:
        if not isinstance(payload["itinerary"], list):
            return None, "itinerary must be a list."
        values["itinerary"] = payload["itinerary"]

    start_date = values.get("start_date")
    end_date = values.get("end_date")
    if start_date and end_date and end_date < start_date:
        return None, "end_date must be on or after start_date."

    return values, None


def _owned_trip(trip_id):
    return Trip.query.filter_by(id=trip_id, user_id=int(g.current_user_id)).first()


@trip_bp.route("", methods=["GET", "POST"])
def trips():
    if request.method == "GET":
        user_trips = Trip.query.filter_by(user_id=int(g.current_user_id)).order_by(Trip.id).all()
        return jsonify([_trip_to_dict(trip) for trip in user_trips]), 200

    values, error = _parse_trip_payload(request.get_json(silent=True))
    if error:
        return jsonify({"error": error}), 400

    trip = Trip(user_id=int(g.current_user_id), **values)
    db.session.add(trip)
    db.session.commit()
    return jsonify(_trip_to_dict(trip)), 201


@trip_bp.route("/<int:trip_id>", methods=["GET", "PUT", "PATCH", "DELETE"])
def trip_detail(trip_id):
    trip = _owned_trip(trip_id)
    if trip is None:
        return jsonify({"error": "Trip not found."}), 404

    if request.method == "GET":
        return jsonify(_trip_to_dict(trip)), 200

    if request.method == "DELETE":
        db.session.delete(trip)
        db.session.commit()
        return "", 204

    values, error = _parse_trip_payload(
        request.get_json(silent=True), partial=request.method == "PATCH"
    )
    if error:
        return jsonify({"error": error}), 400

    updated_start = values.get("start_date", trip.start_date)
    updated_end = values.get("end_date", trip.end_date)
    if updated_end < updated_start:
        return jsonify({"error": "end_date must be on or after start_date."}), 400

    for field, value in values.items():
        setattr(trip, field, value)
    db.session.commit()
    return jsonify(_trip_to_dict(trip)), 200
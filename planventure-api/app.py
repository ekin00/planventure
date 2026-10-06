import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy import text

from auth_middleware import register_auth_middleware
from auth_routes import auth_bp
from extensions import db, jwt
from trip_routes import trip_bp

load_dotenv()

app = Flask(__name__)
database_url = os.getenv("DATABASE_URL", "sqlite:///planventure.db")
if database_url == "your-sqldatabase-url-here":
    database_url = "sqlite:///planventure.db"

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", app.config["SECRET_KEY"])
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# CORS configuration for the React frontend
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
allowed_origins = [origin.strip() for origin in frontend_url.split(",") if origin.strip()]

db.init_app(app)
jwt.init_app(app)
CORS(
    app,
    resources={
        r"/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
        }
    },
)
app.register_blueprint(auth_bp)
app.register_blueprint(trip_bp)
register_auth_middleware(app)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to PlanVenture API"})

@app.route('/health')
def health_check():
    """Basic health check - reports API status and database connectivity."""
    try:
        db.session.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db.session.rollback()
        db_status = "unavailable"

    healthy = db_status == "connected"
    return jsonify({
        "status": "healthy" if healthy else "unhealthy",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }), 200 if healthy else 503

if __name__ == '__main__':
    app.run(debug=True)

import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

from auth_routes import auth_bp
from extensions import db, jwt

load_dotenv()

app = Flask(__name__)
database_url = os.getenv("DATABASE_URL", "sqlite:///planventure.db")
if database_url == "your-sqldatabase-url-here":
    database_url = "sqlite:///planventure.db"

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", app.config["SECRET_KEY"])
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
jwt.init_app(app)
CORS(app)
app.register_blueprint(auth_bp)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to PlanVenture API"})

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(debug=True)

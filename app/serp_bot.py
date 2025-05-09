from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from models import db
from routes import register_routes
from dotenv import load_dotenv
from pathlib import Path
import os

# --- Load .env variables early ---
load_dotenv()

# --- Initialize app ---
app = Flask(__name__)
CORS(app)

# --- Load environment vars ---
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
SSL_CA = os.getenv("SSL_CA")

# --- Build SQLAlchemy URI ---
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ✅ --- SSL Certificate Handling Block ---
if SSL_CA:
    base_dir = Path(__file__).resolve().parent
    ssl_ca_path = str(base_dir / SSL_CA)

    print(f"🔍 Looking for SSL certificate at: {ssl_ca_path}")
    print(f"📄 File exists: {os.path.exists(ssl_ca_path)}")

    if os.path.exists(ssl_ca_path):
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'connect_args': {
                'ssl': {
                    'ca': ssl_ca_path
                }
            }
        }
    else:
        print("⚠️ WARNING: SSL certificate not found. Skipping SSL config.")

# --- Init DB and routes ---
db.init_app(app)
migrate = Migrate(app, db)
register_routes(app)

# --- Error handler ---
@app.errorhandler(Exception)
def handle_error(e):
    return jsonify({"error": str(e)}), 500

# --- App runner ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)

from flask import Flask, jsonify
from flask_cors import CORS
from models import db
from routes import register_routes
import os
from dotenv import load_dotenv
from flask_migrate import Migrate
from pathlib import Path


# Load .env
load_dotenv()

# Get database configuration
DB_URI = os.getenv("DB_URI")
if not DB_URI:
    # If DB_URI is not set, construct it from individual components
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", "25060")
    DB_NAME = os.getenv("DB_NAME")
    SSL_CA = os.getenv("SSL_CA")
    
    # Check required parameters
    if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
        raise ValueError("Missing database configuration. Please set DB_URI or individual DB_* parameters.")
    
    # Construct URI
    DB_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    if SSL_CA:
        DB_URI += f"?ssl_ca={SSL_CA}"

print(f"✅ Using database URI: {DB_URI}")

app = Flask(__name__)
CORS(app)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure SSL if needed
if os.getenv("SSL_CA"):
    ssl_ca_path = str(Path(__file__).resolve().parent / os.getenv("SSL_CA"))
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'connect_args': {
            'ssl': {
                'ca': ssl_ca_path
            }
        }
    }

# Create upload folder
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Init
db.init_app(app)
migrate = Migrate(app, db)
register_routes(app)

@app.errorhandler(Exception)
def handle_error(e):
    return jsonify({"error": str(e)}), 500

# Run
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
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

print("✅ Loaded DB_URI:", os.getenv("DB_URI"))
print("✅ DB_HOST:", os.getenv("DB_HOST"))
print("✅ DB_URI:", os.getenv("DB_URI"))


app = Flask(__name__)
CORS(app)


import os

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
SSL_CA = os.getenv("SSL_CA")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:25060/{DB_NAME}"
    + (f"?ssl_ca={SSL_CA}" if SSL_CA else "")
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False




app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {
        'ssl': {
            'ca': str(Path(__file__).resolve().parent.parent / 'certs' / 'ca-certificate.crt')
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

# === serp_bot.py ===
from flask import Flask,jsonify
from flask_cors import CORS
from models import db
from routes import register_routes
import os
from dotenv import load_dotenv
from flask_migrate import Migrate


# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)



# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
register_routes(app)


@app.errorhandler(Exception)
def handle_error(e):
    return jsonify({"error": str(e)}), 500


# Run server
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)

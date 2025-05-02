from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Client, Job, process_csv
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

@app.route('/clients', methods=['GET'])
def get_clients():
    clients = Client.query.all()
    result = []
    for client in clients:
        job_stats = Job.query.filter_by(client_id=client.id).all()
        total_clicks = sum(job.clicks for job in job_stats)
        active_jobs = any(job.is_active for job in job_stats)
        result.append({
            'id': client.id,
            'name': client.name,
            'active': active_jobs,
            'total_clicks': total_clicks
        })
    return jsonify(result)

@app.route('/clients', methods=['POST'])
def create_client():
    data = request.json
    new_client = Client(name=data['name'])
    db.session.add(new_client)
    db.session.commit()
    return jsonify({'message': 'Client added', 'id': new_client.id})

@app.route('/clients/<int:client_id>/jobs', methods=['GET'])
def get_client_jobs(client_id):
    jobs = Job.query.filter_by(client_id=client_id).all()
    return jsonify([
        {
            'id': job.id,
            'upload_time': job.upload_time,
            'keywords': job.keywords,
            'clicks': job.clicks,
            'is_active': job.is_active,
            'output_logs': job.output_logs
        } for job in jobs
    ])

@app.route('/clients/<int:client_id>/jobs', methods=['POST'])
def upload_csv(client_id):
    file = request.files['file']
    if not file:
        return jsonify({'error': 'No file provided'}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    new_job = process_csv(filepath, client_id)

    return jsonify({'message': 'Job uploaded', 'job_id': new_job.id})

@app.route('/jobs/<int:job_id>/click', methods=['POST'])
def record_click(job_id):
    job = Job.query.get_or_404(job_id)
    job.clicks += 1
    db.session.commit()
    return jsonify({'message': 'Click recorded', 'total_clicks': job.clicks})

@app.route('/jobs/<int:job_id>/deactivate', methods=['POST'])
def deactivate_job(job_id):
    job = Job.query.get_or_404(job_id)
    job.is_active = False
    db.session.commit()
    return jsonify({'message': 'Job deactivated'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Client, Job, ClickEntry
import os
import csv
from flask_cors import CORS
from models import db, Client, Job, ClickEntry
import os
from flask import request, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import logging
import csv
import chardet
import codecs

def register_routes(app: Flask):

    CORS(app)

    UPLOAD_FOLDER = 'uploads'
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

   
    
    @app.route('/jobs/<int:job_id>/clicks', methods=['GET'])
    def get_click_entries(job_id):
        job = Job.query.get_or_404(job_id)
        entries = ClickEntry.query.filter_by(job_id=job.id).all()
        return jsonify([
            {
                'keyword': entry.keyword,
                'dwell_time': entry.dwell_time
            } for entry in entries
        ])

    @app.route('/jobs/<int:job_id>', methods=['GET'])
    def get_job_details(job_id):
        job = Job.query.get_or_404(job_id)
        client = Client.query.get(job.client_id)
        return jsonify({
            'id': job.id,
            'name': job.name,
            'client_id': job.client_id,
            'client_name': client.name if client else "Unknown",
            'upload_time': job.upload_time.isoformat(),
            'keywords': job.keywords,
            'clicks': job.clicks,
            'is_active': job.is_active,
            'output_logs': job.output_logs
        })
    @app.route('/clients/name/<name>', methods=['GET'])
    def get_client_by_name(name):
        cleaned_name = name.strip()
        client = Client.query.filter(Client.name.ilike(f"%{cleaned_name}%")).first()
        if client:
            return jsonify({'id': client.id, 'name': client.name})
        return jsonify({'error': 'Client not found'}), 404
 
    @app.route('/clients/<int:client_id>', methods=['GET'])
    def fetch_client_by_id(client_id):  # ← changed name
        client = Client.query.get_or_404(client_id)
        return jsonify({'id': client.id, 'name': client.name})


    



    @app.route('/clients', methods=['POST'])
    def create_client():
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'Client name required'}), 400
        new_client = Client(name=data['name'])
        db.session.add(new_client)
        db.session.commit()
        return jsonify({'message': 'Client added', 'id': new_client.id}), 201

    @app.route('/clients/<int:client_id>/jobs', methods=['GET'])
    def get_client_jobs(client_id):
        jobs = Job.query.filter_by(client_id=client_id).all()
        return jsonify([
            {
                'id': job.id,
                'name': job.name,
                'upload_time': job.upload_time.isoformat(),
                'keywords': job.keywords,
                'clicks': job.clicks,
                'is_active': job.is_active,
                'output_logs': job.output_logs
            } for job in jobs
        ])

    @app.route('/clients/<int:client_id>/jobs/add', methods=['POST'])
    def add_job(client_id):
        data = request.get_json()
        if not data or 'name' not in data or 'keywords' not in data:
            return jsonify({'error': 'Name and keywords are required'}), 400

        keyword_string = ",".join(data['keywords'])  # Convert list to comma-separated string

        new_job = Job(
            name=data['name'],
            keywords=keyword_string,
            client_id=client_id,
            output_logs=data.get('output_logs', 'Job created manually'),
            is_active=False,
            bot_status='inactive'
        )

        db.session.add(new_job)
        db.session.commit()

        return jsonify({'message': 'Job added', 'job_id': new_job.id,'name':new_job.name}), 201


    @app.route('/jobs/<int:job_id>', methods=['DELETE'])
    def delete_job(job_id):
        job = Job.query.get_or_404(job_id)
        db.session.delete(job)
        db.session.commit()
        return jsonify({'message': f'Job {job_id} deleted'}), 200

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

   
    
    @app.route('/jobs/<int:job_id>/upload', methods=['POST'])
    def upload_job_csv(job_id):
        job = Job.query.get_or_404(job_id)

        if 'file' not in request.files:
            return jsonify({'error': 'CSV file required'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        if not file.filename.lower().endswith('.csv'):
            return jsonify({'error': 'Only CSV files are allowed'}), 400

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        try:
            # Try reading with utf-8, fallback to ISO-8859-1
            try:
                with open(filepath, newline='', encoding='utf-8') as csvfile:
                    rows = list(csv.reader(csvfile))
            except UnicodeDecodeError:
                with open(filepath, newline='', encoding='ISO-8859-1') as csvfile:
                    rows = list(csv.reader(csvfile))

            # Clear old entries for this job
            ClickEntry.query.filter_by(job_id=job.id).delete()

            for row in rows:
                if not row:
                    continue
                keyword = row[0].strip()
                dwell_time = int(row[1]) if len(row) > 1 and row[1].isdigit() else None
                if len(keyword) > 255:
                    keyword = keyword[:255]
                entry = ClickEntry(job_id=job.id, keyword=keyword, dwell_time=dwell_time)
                db.session.add(entry)

            job.csv_filename = file.filename
            job.bot_output = 'Bot ran successfully and output logged.'
            job.output_logs = f'CSV processed from {file.filename}'
            job.bot_status = 'completed'
            job.is_active = False

            db.session.commit()
            return jsonify({'message': 'CSV uploaded and data saved to DB'}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
    @app.route("/jobs/<int:job_id>/run-bot", methods=["POST"])
    def run_bot_simulation(job_id):
        job = Job.query.get_or_404(job_id)

        # Update status of each entry
        entries = ClickEntry.query.filter_by(job_id=job.id).all()
        for entry in entries:
            entry.status = "clicked"
        db.session.commit()

        # Re-fetch after commit (fresh from DB)
        updated_entries = ClickEntry.query.filter_by(job_id=job.id).all()

        return jsonify([
            {
                "keyword": e.keyword,
                "dwell_time": e.dwell_time,
                "status": e.status
            } for e in updated_entries
        ])

    @app.route('/jobs/<int:job_id>/activate', methods=['POST'])
    def activate_job(job_id):
        job = Job.query.get_or_404(job_id)
        job.is_active = True
        job.bot_status = 'active'
        db.session.commit()
        return jsonify({'message': 'Job activated'})


    @app.route('/jobs/<int:job_id>/deactivate', methods=['POST'])
    def deactivate_job(job_id):
        job = Job.query.get_or_404(job_id)
        job.is_active = False
        job.bot_status = 'inactive'
        db.session.commit()
        return jsonify({'message': 'Job deactivated'})


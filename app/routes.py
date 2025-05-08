def register_routes(app):
    from flask_cors import CORS
    from models import db, Client, Job, process_csv
    import os
    from flask import request, jsonify
    from dotenv import load_dotenv
    import logging
    

    load_dotenv()
    CORS(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    UPLOAD_FOLDER = 'uploads'
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

        new_job = Job(
                name=data['name'],
                keywords=data['keywords'],
                client_id=client_id,
                output_logs=data.get('output_logs', 'Job created manually'),
                is_active=False,
                bot_status='inactive'
            )
        db.session.add(new_job)
        db.session.commit()

        return jsonify({'message': 'Job added', 'job_id': new_job.id}), 201


    @app.route('/jobs/<int:job_id>', methods=['DELETE'])
    def delete_job(job_id):
        job = Job.query.get_or_404(job_id)
        db.session.delete(job)
        db.session.commit()
        return jsonify({'message': f'Job {job_id} deleted'}), 200


    @app.route('/jobs/<int:job_id>/upload', methods=['POST'])
    def upload_job_csv(job_id):
        job = Job.query.get_or_404(job_id)

        if 'file' not in request.files:
            return jsonify({'error': 'CSV file required'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        try:
            job.csv_filename = file.filename
            job.bot_output = 'Bot ran successfully and output logged.'
            job.output_logs = f'CSV processed from {file.filename}'
            job.bot_status = 'completed'
            job.is_active = False
            db.session.commit()
            return jsonify({'message': 'CSV uploaded and job updated'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500


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


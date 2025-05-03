def register_routes(app):
    from flask_cors import CORS
    from models import db, Client, Job, process_csv
    import os
    from flask import request, jsonify
    from dotenv import load_dotenv

    load_dotenv()
    CORS(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'uploads'
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


    @app.route('/clients', methods=['GET'])
    def get_clients():
        ...

    @app.route('/clients', methods=['POST'])
    def create_client():
        ...

    @app.route('/clients/<int:client_id>/jobs', methods=['GET'])
    def get_client_jobs(client_id):
        ...

    @app.route('/clients/<int:client_id>/jobs', methods=['POST'])
    def upload_csv(client_id):
        ...

    @app.route('/jobs/<int:job_id>/click', methods=['POST'])
    def record_click(job_id):
        ...

    @app.route('/jobs/<int:job_id>/deactivate', methods=['POST'])
    def deactivate_job(job_id):
        ...

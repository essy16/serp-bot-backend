from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import csv

# Initialize SQLAlchemy
db = SQLAlchemy()

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    jobs = db.relationship('Job', backref='client', lazy=True)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(100), nullable=False)
    keywords = db.Column(db.String(500), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    csv_filename = db.Column(db.String(255), nullable=True)
    bot_output = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=False)
    bot_status = db.Column(db.String(50), default='inactive')
    clicks = db.Column(db.Integer, default=0)
    output_logs = db.Column(db.Text, nullable=True)


def process_csv(file_path, client_id):
    keywords = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row:
                keywords.append(row[0])

    keyword_string = ','.join(keywords[:50])
    new_job = Job(
        client_id=client_id,
        keywords=keyword_string,
        output_logs='CSV processed via process_csv()',
        is_active=True
    )
    db.session.add(new_job)
    db.session.commit()
    return new_job
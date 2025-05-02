from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pymysql
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
    keywords = db.Column(db.String(500), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    output_logs = db.Column(db.Text, nullable=True)
    clicks = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=False)

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


def create_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        db='clients_jobs_db'
    )

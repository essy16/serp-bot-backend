import os
import pymysql
import ssl
from dotenv import load_dotenv

load_dotenv()

DB_HOST = "client-job-db-do-user-20060435-0.l.db.ondigitalocean.com"
DB_PORT = 25060
DB_USER = "doadmin"
DB_PASSWORD = ""
SSL_CA =os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'certs', 'ca-certificate.crt'))


try:
    connection = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        ssl={'ca': SSL_CA}
    )

    with connection.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS clients_jobs_db;")
        print("✅ Database 'clients_jobs_db' created or already exists.")

    connection.close()

except Exception as e:
    print(f"❌ Failed to create database: {e}")
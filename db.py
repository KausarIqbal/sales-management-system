import os
import psycopg2

def get_connection():
    conn = psycopg2.connect(
        host=os.getenv("DBHOST"),
        database=os.getenv("DBNAME"),
        user=os.getenv("DBUSER"),
        password=os.getenv("DBPASSWORD"),
        port=os.getenv("DBPORT")
    )
    return conn

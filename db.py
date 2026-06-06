import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="mysql.railway.internal",
        user="root",
        password="rPWoSRddtYmKrdSimpJryopXuWKrccwL",
        database="railway",
        port=3306
    )
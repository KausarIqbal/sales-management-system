import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="_#Harlick_1",
        database="sales_system"
    )
import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '7efnawinn591911',
    'database': 'ClinicDB'
}

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [x[0] for x in cursor.fetchall()]
    print(f"Tables found: {tables}")
    conn.close()
except Exception as e:
    print(f"Error: {e}")

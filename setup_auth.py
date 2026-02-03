import mysql.connector
import hashlib

# Connection settings
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '7efnawinn591911',
    'database': 'ClinicDB'
}

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def setup_auth():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # 1. Create Users Table
        print("Creating Users table...")
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS Users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(100),
            role ENUM('Admin', 'Doctor', 'Secretary') DEFAULT 'Secretary',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(create_table_sql)
        
        # 2. Insert Default Admin
        print("Inserting Admin user...")
        admin_user = "admin"
        admin_pass = "admin123"
        admin_hash = hash_password(admin_pass)
        
        insert_sql = """
        INSERT INTO Users (username, password_hash, full_name, role)
        VALUES (%s, %s, %s, 'Admin')
        ON DUPLICATE KEY UPDATE password_hash = VALUES(password_hash)
        """
        cursor.execute(insert_sql, (admin_user, admin_hash, "System Administrator"))
        
        conn.commit()
        print("✅ Success! Users table created and Admin (admin/admin123) added.")
        
        cursor.close()
        conn.close()
        
    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")

if __name__ == "__main__":
    setup_auth()

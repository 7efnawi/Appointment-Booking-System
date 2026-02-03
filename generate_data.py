import mysql.connector
from faker import Faker
import random
from datetime import datetime, timedelta

# ==========================================
# Connection settings (Edit the password)
# ==========================================
db_config = {
    'host': 'localhost',
    'user': 'root',          # or the user you prefer
    'password': '7efnawinn591911', # <--- Place your server password here
    'database': 'ClinicDB'
}

fake = Faker()
Faker.seed(0) # To ensure consistent random data for testing

def create_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def generate_data():
    conn = create_connection()
    if not conn:
        return
    cursor = conn.cursor()

    print("🚀 Starting Data Generation...")

    # ---------------------------------------------------
    # 1. Insert Specialists
    # ---------------------------------------------------
    print("1. Inserting Specialists...")
    specialties_list = [
        ('General Practice', 'Routine checkups'), 
        ('Cardiology', 'Heart specialists'), 
        ('Dermatology', 'Skin care'), 
        ('Pediatrics', 'Children health'), 
        ('Orthopedics', 'Bones and muscles')
    ]
    
    # Use INSERT IGNORE to avoid errors if data already exists
    sql_spec = "INSERT IGNORE INTO Specialists (speciality_name, description) VALUES (%s, %s)"
    cursor.executemany(sql_spec, specialties_list)
    conn.commit()

    # Fetch specialties to link doctors to them
    cursor.execute("SELECT speciality_id FROM Specialists")
    spec_ids = [row[0] for row in cursor.fetchall()]

    # ---------------------------------------------------
    # 2. Insert Doctors
    # ---------------------------------------------------
    print("2. Generating 15 Doctors...")
    for _ in range(15):
        first_name = fake.first_name()
        last_name = fake.last_name()
        spec_id = random.choice(spec_ids)
        phone = fake.phone_number()[:15] # Truncate phone number to fit column size
        email = fake.email()
        fee = round(random.uniform(50.0, 300.0), 2)
        
        sql_doc = """
        INSERT INTO Doctors (first_name, last_name, specialty_id, phone, email, consultation_fee)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql_doc, (first_name, last_name, spec_id, phone, email, fee))
    conn.commit()
    
    # Fetch doctor IDs
    cursor.execute("SELECT doctor_id, consultation_fee FROM Doctors")
    doctors = cursor.fetchall() # List containing (id, fee)

    # ---------------------------------------------------
    # 3. Insert Patients
    # ---------------------------------------------------
    print("3. Generating 100 Patients...")
    patient_ids = []
    for _ in range(100):
        f_name = fake.first_name()
        l_name = fake.last_name()
        dob = fake.date_of_birth(minimum_age=2, maximum_age=90)
        gender = random.choice(['Male', 'Female'])
        phone = fake.unique.phone_number()[:15]
        address = fake.address()
        
        sql_pat = """
        INSERT INTO Patients (first_name, last_name, date_of_birth, gender, phone, address)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql_pat, (f_name, l_name, dob, gender, phone, address))
    conn.commit()
    
    cursor.execute("SELECT patient_id FROM Patients")
    patient_ids = [row[0] for row in cursor.fetchall()]

    # ---------------------------------------------------
    # 4. Insert Appointments
    # ---------------------------------------------------
    print("4. Generating 300 Appointments...")
    appt_ids = []
    
    # To avoid duplicate appointments for the same doctor, generating random appointments and trying to insert them
    for _ in range(300):
        doc = random.choice(doctors)
        doc_id = doc[0]
        pat_id = random.choice(patient_ids)
        
        # Random date within the last two months and the next month
        appt_date = fake.date_between(start_date='-60d', end_date='+30d')
        # Working hours from 9 AM to 5 PM
        appt_hour = random.randint(9, 17)
        appt_time = f"{appt_hour}:00:00"
        
        status = random.choices(
            ['Scheduled', 'Completed', 'Cancelled', 'No-Show'], 
            weights=[40, 40, 10, 10], k=1
        )[0]
        
        try:
            sql_appt = """
            INSERT INTO Appointments (patient_id, doctor_id, appointment_date, appointment_time, status)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql_appt, (pat_id, doc_id, appt_date, appt_time, status))
            
            # If successful, get the ID for the invoice
            appt_id = cursor.lastrowid
            
            # ---------------------------------------------------
            # 5. Insert Invoices (Only for Completed)
            # ---------------------------------------------------
            if status == 'Completed':
                amount = doc[1] # Doctor's consultation fee
                payment = random.choice(['Cash', 'Credit Card', 'Insurance'])
                sql_inv = "INSERT INTO Invoices (appointment_id, amount, payment_method) VALUES (%s, %s, %s)"
                cursor.execute(sql_inv, (appt_id, amount, payment))
                
        except mysql.connector.errors.IntegrityError:
            # If appointment collision happens, ignore and continue
            continue

    conn.commit()
    print("✅ Success! Database populated with dummy data.")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    generate_data()
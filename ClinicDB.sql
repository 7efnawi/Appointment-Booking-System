-- Create the database
CREATE DATABASE IF NOT EXISTS ClinicDB
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE ClinicDB;

CREATE TABLE IF NOT EXISTS Specialists (
   speciality_id INT AUTO_INCREMENT PRIMARY KEY,
   speciality_name VARCHAR(100) UNIQUE NOT NULL,
   description TEXT
);

CREATE TABLE IF NOT EXISTS Doctors (
   doctor_id INT AUTO_INCREMENT PRIMARY KEY,
   first_name VARCHAR(50) NOT NULL,
   last_name VARCHAR(50) NOT NULL,
   specialty_id INT,
   phone VARCHAR(20) NOT NULL,
   email VARCHAR(100) NOT NULL,
   consultation_fee DECIMAL(10, 2) DEFAULT 0.00,
   join_date DATE DEFAULT CURRENT_TIMESTAMP,
   FOREIGN KEY (specialty_id) REFERENCES Specialists(speciality_id)
);

CREATE TABLE IF NOT EXISTS Doctor_Schedule (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    doctor_id INT,
    day_of_week ENUM('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (doctor_id) REFERENCES Doctors(doctor_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Patients (
   patient_id INT AUTO_INCREMENT PRIMARY KEY,
   first_name VARCHAR(50) NOT NULL,
   last_name VARCHAR(50) NOT NULL,
   date_of_birth DATE NOT NULL,
   gender ENUM('Male', 'Female') NOT NULL,
   phone VARCHAR(20) NOT NULL,
   address VARCHAR(255),
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Appointments (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    doctor_id INT,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    status ENUM('Scheduled', 'Completed', 'Cancelled', 'No-Show') DEFAULT 'Scheduled',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES Doctors(doctor_id),
    
    UNIQUE KEY unique_booking (doctor_id, appointment_date, appointment_time)
);

CREATE TABLE IF NOT EXISTS Invoices (
    invoice_id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT UNIQUE, 
    amount DECIMAL(10, 2) NOT NULL,
    payment_method ENUM('Cash', 'Credit Card', 'Insurance') DEFAULT 'Cash',
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (appointment_id) REFERENCES Appointments(appointment_id)
);

-- View 1: 
CREATE VIEW View_All_Appointment_Details AS
SELECT 
    A.appointment_id,
    CONCAT(P.first_name, ' ', P.last_name) AS Patient_Name,
    P.phone AS Patient_Phone,
    CONCAT(D.first_name, ' ', D.last_name) AS Doctor_Name,
    S.speciality_name,
    A.appointment_date,
    A.appointment_time,
    A.status,
    I.amount AS Invoice_Amount,
    I.payment_method
FROM Appointments A
JOIN Patients P ON A.patient_id = P.patient_id
JOIN Doctors D ON A.doctor_id = D.doctor_id
JOIN Specialists S ON D.specialty_id = S.speciality_id
LEFT JOIN Invoices I ON A.appointment_id = I.appointment_id;

-- View 2
CREATE VIEW View_Financial_Summary AS
SELECT 
    DATE_FORMAT(payment_date, '%Y-%m') AS Month,
    payment_method,
    COUNT(invoice_id) AS Transaction_Count,
    SUM(amount) AS Total_Revenue
FROM Invoices
GROUP BY Month, payment_method;

-- ============================================
-- ADDITIONAL TABLES FOR APP.PY
-- ============================================

-- Users Table (Authentication)
CREATE TABLE IF NOT EXISTS Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(64) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('Admin', 'Doctor', 'Secretary') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Default Admin User (Password: admin123)
INSERT IGNORE INTO Users (username, password_hash, full_name, role) VALUES
('admin', SHA2('admin123', 256), 'System Administrator', 'Admin');

-- Consultations Table (Medical Records)
CREATE TABLE IF NOT EXISTS Consultations (
    consultation_id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT NOT NULL,
    symptoms TEXT,
    diagnosis TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (appointment_id) REFERENCES Appointments(appointment_id) ON DELETE CASCADE
);

-- Prescriptions Table
CREATE TABLE IF NOT EXISTS Prescriptions (
    prescription_id INT AUTO_INCREMENT PRIMARY KEY,
    consultation_id INT NOT NULL,
    medication_name VARCHAR(255),
    dosage VARCHAR(100),
    duration VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (consultation_id) REFERENCES Consultations(consultation_id) ON DELETE CASCADE
);
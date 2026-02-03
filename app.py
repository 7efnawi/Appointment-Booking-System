"""
Clinic Pro System - Production Ready v2.0
==========================================
A comprehensive clinic management system built with Streamlit and MySQL.

Features:
- Role-based access control (Admin, Doctor, Secretary)
- Patient registration and management
- Appointment booking with double-booking prevention
- Doctor consultation workflow with diagnosis and prescriptions
- Automated invoicing
- Executive BI Dashboard with analytics

Author: Clinic Pro Development Team
"""

import streamlit as st
import mysql.connector
from mysql.connector import pooling
import pandas as pd
import datetime
import hashlib
import plotly.express as px
from streamlit_option_menu import option_menu

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Clinic Pro System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. SESSION STATE INITIALIZATION
# ==========================================
# Initialize all session state variables at the start
DEFAULT_STATE = {
    'logged_in': False,
    'user_role': None,
    'username': None,
    'user_id': None,
    'page_selection': 0
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ==========================================
# 3. CUSTOM CSS STYLING
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Metric Cards */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    div[data-testid="metric-container"] label {
        color: rgba(255,255,255,0.8) !important;
    }
    
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: white !important;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 25px;
        font-weight: 600;
        padding: 0.5rem 2rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* DataFrames */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    /* Form Containers */
    [data-testid="stForm"] {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e9ecef;
    }
    
    /* Success/Error Messages */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 8px;
    }
    
    /* Enhanced Expander Boxes */
    [data-testid="stExpander"] {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.12);
        margin-bottom: 1.5rem;
        background: linear-gradient(145deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stExpander"] > details {
        border: none !important;
        background: transparent;
    }
    
    [data-testid="stExpander"] > details > summary {
        background: linear-gradient(135deg, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0.05) 100%);
        color: white !important;
        font-weight: 600;
        font-size: 1.1rem;
        padding: 1.2rem 1.5rem;
        border-radius: 16px;
        transition: all 0.3s ease;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    [data-testid="stExpander"] > details > summary:hover {
        background: linear-gradient(135deg, rgba(255,255,255,0.25) 0%, rgba(255,255,255,0.1) 100%);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
    }
    
    [data-testid="stExpander"] > details > summary svg {
        fill: white !important;
    }
    
    [data-testid="stExpander"] > details > summary p {
        color: white !important;
    }
    
    [data-testid="stExpander"] > details[open] > summary {
        border-radius: 16px 16px 0 0;
        border-bottom: 1px solid rgba(255,255,255,0.15);
    }
    
    [data-testid="stExpander"] > details > div {
        background: #f8f9fc;
        border-radius: 0 0 16px 16px;
        padding: 1.5rem;
    }
    
    /* Colorful Input Fields */
    [data-testid="stExpander"] input[type="text"],
    [data-testid="stExpander"] input[type="number"],
    [data-testid="stExpander"] input[type="date"],
    [data-testid="stExpander"] input[type="time"],
    [data-testid="stExpander"] input[type="password"],
    [data-testid="stExpander"] textarea {
        background: white !important;
        border: 2px solid #667eea !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        font-size: 1rem !important;
        color: #1a1a2e !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stExpander"] input:focus,
    [data-testid="stExpander"] textarea:focus {
        border-color: #764ba2 !important;
        box-shadow: 0 0 0 3px rgba(118, 75, 162, 0.2) !important;
    }
    
    /* Select Dropdowns - Dark background with white text */
    [data-testid="stExpander"] [data-baseweb="select"] > div:first-child {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border-radius: 10px !important;
        border: none !important;
    }
    
    [data-testid="stExpander"] [data-baseweb="select"] [data-baseweb="tag"] {
        background: rgba(255,255,255,0.2) !important;
    }
    
    [data-testid="stExpander"] [data-baseweb="select"] span,
    [data-testid="stExpander"] [data-baseweb="select"] div[class*="valueContainer"] {
        color: white !important;
    }
    
    [data-testid="stExpander"] [data-baseweb="select"] svg {
        fill: white !important;
    }
    
    /* Primary Buttons in Forms */
    [data-testid="stExpander"] button[kind="primary"],
    [data-testid="stExpander"] button[type="submit"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stExpander"] button[kind="primary"]:hover,
    [data-testid="stExpander"] button[type="submit"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
    }
    
    /* Date Input Container */
    [data-testid="stExpander"] [data-testid="stDateInput"] input {
        color: #1a1a2e !important;
        background: white !important;
    }
    
    /* Labels inside expanders */
    [data-testid="stExpander"] label {
        color: #2c3e50 !important;
        font-weight: 500 !important;
    }
    
    /* Multi-select placeholder text */
    [data-testid="stExpander"] [data-baseweb="select"] [class*="placeholder"] {
        color: rgba(255,255,255,0.8) !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. DATABASE CONNECTION (SECURE)
# ==========================================
@st.cache_resource
def get_db_connection():
    """
    Secure database connection using st.secrets.
    Falls back to environment-based config for local development.
    """
    try:
        # PRIMARY: Use Streamlit Secrets (Production)
        if "mysql" in st.secrets:
            config = dict(st.secrets["mysql"])
        else:
            # DEVELOPMENT ONLY: Local config
            # In production, this should raise an error
            config = {
                'host': 'localhost',
                'user': 'root',
                'password': '7efnawinn591911',
                'database': 'ClinicDB'
            }
        
        # Create connection with auto-reconnect
        conn = mysql.connector.connect(
            **config,
            autocommit=False,
            connection_timeout=30
        )
        return conn
    
    except mysql.connector.Error as err:
        st.error(f"❌ Database Connection Failed: {err}")
        st.info("Please check your database configuration and ensure MySQL is running.")
        st.stop()

def get_connection():
    """Get a fresh connection, handling reconnection if needed."""
    conn = get_db_connection()
    try:
        conn.ping(reconnect=True, attempts=3, delay=2)
    except mysql.connector.Error:
        st.cache_resource.clear()
        conn = get_db_connection()
    return conn

def run_query(query, params=None):
    """
    Execute INSERT/UPDATE/DELETE operations with proper error handling.
    Returns the last inserted ID for INSERT operations.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        last_id = cursor.lastrowid
        cursor.close()
        return last_id
    except mysql.connector.Error as err:
        st.error(f"❌ Database Error: {err}")
        return None

def load_data(query, params=None):
    """
    Execute SELECT queries and return results as a DataFrame.
    """
    try:
        conn = get_connection()
        return pd.read_sql(query, conn, params=params)
    except Exception as err:
        st.error(f"❌ Query Error: {err}")
        return pd.DataFrame()

@st.cache_data(ttl=600)
def get_cached_data(query):
    """
    Cached data fetching for static/slowly changing data (e.g., dropdowns).
    TTL: 10 minutes
    """
    try:
        conn = get_connection()
        return pd.read_sql(query, conn)
    except Exception:
        return pd.DataFrame()

# ==========================================
# 5. AUTHENTICATION MODULE
# ==========================================
def hash_password(password):
    """Generate SHA-256 hash of password."""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username, password):
    """Verify user credentials and return user data if valid."""
    pwd_hash = hash_password(password)
    query = """
        SELECT user_id, username, full_name, role 
        FROM Users 
        WHERE username = %s AND password_hash = %s
    """
    result = load_data(query, (username, pwd_hash))
    return result.iloc[0].to_dict() if not result.empty else None

def logout():
    """Clear all session state and force re-login."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# ==========================================
# 6. LOGIN SCREEN
# ==========================================
if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
            <div style='text-align: center; padding: 40px;'>
                <h1 style='color: #2c3e50; margin-bottom: 10px;'>🏥 Clinic Pro</h1>
                <p style='color: #7f8c8d; font-size: 1.1rem;'>Healthcare Management System</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                login_submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")
            
            if login_submitted:
                if username and password:
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state['logged_in'] = True
                        st.session_state['user_id'] = user['user_id']
                        st.session_state['username'] = user['full_name']
                        st.session_state['user_role'] = user['role']
                        st.success(f"Welcome, {user['full_name']}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                else:
                    st.warning("⚠️ Please enter both username and password")
    
    st.stop()

# ==========================================
# 7. NAVIGATION SIDEBAR
# ==========================================
role = st.session_state['user_role']

# Define role-based menu access
MENU_CONFIG = {
    'Admin': {
        'options': ["Dashboard", "Patients", "Doctors", "Appointments", "Users"],
        'icons': ["graph-up-arrow", "people", "person-badge", "calendar-event", "gear"]
    },
    'Doctor': {
        'options': ["My Schedule", "Patients"],
        'icons': ["calendar-check", "people"]
    },
    'Secretary': {
        'options': ["Appointments", "Patients"],
        'icons': ["calendar-event", "people"]
    }
}

current_menu = MENU_CONFIG.get(role, MENU_CONFIG['Secretary'])

with st.sidebar:
    # User Info
    st.markdown(f"""
        <div style='text-align: center; padding: 20px 0;'>
            <div style='font-size: 3rem;'>👨‍⚕️</div>
            <h3 style='margin: 10px 0 5px 0;'>{st.session_state['username']}</h3>
            <span style='background-color: #1abc9c; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem;'>{role}</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Navigation Menu
    selected = option_menu(
        menu_title=None,
        options=current_menu['options'],
        icons=current_menu['icons'],
        default_index=min(st.session_state.get('page_selection', 0), len(current_menu['options']) - 1),
        key='nav_menu',
        styles={
            "container": {"padding": "0", "background-color": "transparent"},
            "icon": {"color": "#3498db", "font-size": "18px"},
            "nav-link": {
                "font-size": "15px",
                "text-align": "left",
                "margin": "5px 0",
                "padding": "12px 15px",
                "border-radius": "8px",
                "--hover-color": "#ecf0f1"
            },
            "nav-link-selected": {
                "background-color": "#3498db",
                "color": "white"
            }
        }
    )
    
    # Update page selection in session
    if selected in current_menu['options']:
        st.session_state['page_selection'] = current_menu['options'].index(selected)
    
    st.divider()
    
    # Logout Button
    if st.button("🚪 Log Out", use_container_width=True):
        logout()

# ==========================================
# 8. PAGE: DASHBOARD (Admin Only)
# ==========================================
if selected == "Dashboard":
    if role != "Admin":
        st.error("⛔ Access Denied: Admin privileges required")
        st.stop()
    
    st.title("📊 Executive Dashboard")
    st.caption("Real-time clinic performance analytics")
    
    # Date Filters
    with st.expander("📅 Filter Options", expanded=True):
        with st.form("dashboard_filters"):
            col1, col2, col3 = st.columns(3)
            today = datetime.date.today()
            
            with col1:
                start_date = st.date_input("Start Date", today.replace(day=1))
            with col2:
                end_date = st.date_input("End Date", today)
            with col3:
                doctor_df = get_cached_data("SELECT doctor_id, CONCAT(first_name, ' ', last_name) as name FROM Doctors")
                selected_doctors = st.multiselect("Filter by Doctor", doctor_df['name'].tolist() if not doctor_df.empty else [])
            
            st.form_submit_button("Apply Filters", use_container_width=True)
    
    # Fetch Data
    query = """
        SELECT 
            a.appointment_date,
            a.status,
            COALESCE(i.amount, 0) as amount,
            CONCAT(d.first_name, ' ', d.last_name) as doctor_name
        FROM Appointments a
        JOIN Doctors d ON a.doctor_id = d.doctor_id
        LEFT JOIN Invoices i ON a.appointment_id = i.appointment_id
        WHERE a.appointment_date BETWEEN %s AND %s
    """
    df = load_data(query, (start_date, end_date))
    
    if not df.empty:
        # Apply doctor filter if selected
        if selected_doctors:
            df = df[df['doctor_name'].isin(selected_doctors)]
        
        # KPI Metrics
        st.markdown("### 📈 Key Performance Indicators")
        k1, k2, k3, k4 = st.columns(4)
        
        total_revenue = df['amount'].sum()
        total_appointments = len(df)
        cancelled = len(df[df['status'] == 'Cancelled'])
        completed = len(df[df['status'] == 'Completed'])
        
        cancel_rate = (cancelled / total_appointments * 100) if total_appointments > 0 else 0
        completion_rate = (completed / total_appointments * 100) if total_appointments > 0 else 0
        
        k1.metric("💰 Total Revenue", f"${total_revenue:,.2f}")
        k2.metric("📅 Appointments", total_appointments)
        k3.metric("❌ Cancellation Rate", f"{cancel_rate:.1f}%")
        k4.metric("✅ Completion Rate", f"{completion_rate:.1f}%")
        
        st.divider()
        
        # Charts Row 1
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Revenue Trend")
            daily_revenue = df.groupby('appointment_date')['amount'].sum().reset_index()
            if not daily_revenue.empty:
                fig = px.area(daily_revenue, x='appointment_date', y='amount',
                             color_discrete_sequence=['#3498db'])
                fig.update_layout(xaxis_title="Date", yaxis_title="Revenue ($)")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Status Distribution")
            status_counts = df['status'].value_counts().reset_index()
            status_counts.columns = ['status', 'count']
            fig = px.pie(status_counts, values='count', names='status', hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig, use_container_width=True)
        
        # Top Doctors
        st.subheader("🏆 Top Performing Doctors")
        doc_revenue = df.groupby('doctor_name')['amount'].sum().reset_index()
        doc_revenue = doc_revenue.sort_values('amount', ascending=True).tail(5)
        fig = px.bar(doc_revenue, x='amount', y='doctor_name', orientation='h',
                    color='amount', color_continuous_scale='Blues',
                    text_auto='.2s')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("📭 No data available for the selected period.")

# ==========================================
# 9. PAGE: MY SCHEDULE (Doctor Only)
# ==========================================
elif selected == "My Schedule":
    if role != "Doctor":
        st.error("⛔ Access Denied: Doctor privileges required")
        st.stop()
    
    st.title("🩺 My Consultation Queue")
    st.caption(f"Today's schedule: {datetime.date.today().strftime('%A, %B %d, %Y')}")
    
    # Find doctor ID linked to current user
    user_name = st.session_state['username']
    name_parts = user_name.split()
    
    if len(name_parts) >= 2:
        first_name, last_name = name_parts[0], name_parts[-1]
        doc_query = """
            SELECT doctor_id, consultation_fee 
            FROM Doctors 
            WHERE first_name LIKE %s AND last_name LIKE %s
        """
        doc_result = load_data(doc_query, (f"%{first_name}%", f"%{last_name}%"))
        
        if not doc_result.empty:
            doctor_id = doc_result.iloc[0]['doctor_id']
            consultation_fee = doc_result.iloc[0]['consultation_fee']
            
            # Fetch today's appointments
            today = datetime.date.today()
            appt_query = """
                SELECT 
                    a.appointment_id,
                    a.appointment_time,
                    a.status,
                    p.patient_id,
                    CONCAT(p.first_name, ' ', p.last_name) as patient_name,
                    p.gender,
                    TIMESTAMPDIFF(YEAR, p.date_of_birth, CURDATE()) as age,
                    p.phone
                FROM Appointments a
                JOIN Patients p ON a.patient_id = p.patient_id
                WHERE a.doctor_id = %s AND a.appointment_date = %s
                ORDER BY a.appointment_time ASC
            """
            appointments = load_data(appt_query, (doctor_id, today))
            
            if not appointments.empty:
                # Summary Cards
                total = len(appointments)
                pending = len(appointments[appointments['status'] == 'Scheduled'])
                completed = len(appointments[appointments['status'] == 'Completed'])
                
                c1, c2, c3 = st.columns(3)
                c1.metric("📋 Total", total)
                c2.metric("⏳ Pending", pending)
                c3.metric("✅ Completed", completed)
                
                st.divider()
                
                # Appointment Cards
                for _, appt in appointments.iterrows():
                    status_color = {
                        'Scheduled': '🟡',
                        'Completed': '🟢',
                        'Cancelled': '🔴'
                    }.get(appt['status'], '⚪')
                    
                    with st.expander(
                        f"{status_color} {appt['appointment_time']} - {appt['patient_name']}",
                        expanded=(appt['status'] == 'Scheduled')
                    ):
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            st.markdown("#### 👤 Patient Info")
                            st.write(f"**Name:** {appt['patient_name']}")
                            st.write(f"**Age:** {appt['age']} years")
                            st.write(f"**Gender:** {appt['gender']}")
                            st.write(f"**Phone:** {appt['phone']}")
                            st.info(f"**Status:** {appt['status']}")
                        
                        with col2:
                            if appt['status'] == 'Completed':
                                st.success("✅ This visit has been completed.")
                                
                                # Show existing consultation
                                cons_query = """
                                    SELECT c.symptoms, c.diagnosis, c.notes,
                                           GROUP_CONCAT(CONCAT(pr.medication_name, ' - ', pr.dosage, ' for ', pr.duration) SEPARATOR '\n') as prescriptions
                                    FROM Consultations c
                                    LEFT JOIN Prescriptions pr ON c.consultation_id = pr.consultation_id
                                    WHERE c.appointment_id = %s
                                    GROUP BY c.consultation_id
                                """
                                cons_data = load_data(cons_query, (appt['appointment_id'],))
                                if not cons_data.empty:
                                    st.write("**📋 Previous Notes:**")
                                    st.write(f"*Symptoms:* {cons_data.iloc[0]['symptoms']}")
                                    st.write(f"*Diagnosis:* {cons_data.iloc[0]['diagnosis']}")
                                    if cons_data.iloc[0]['prescriptions']:
                                        st.write(f"*Prescriptions:* {cons_data.iloc[0]['prescriptions']}")
                                        
                            elif appt['status'] == 'Cancelled':
                                st.warning("❌ This appointment was cancelled.")
                                
                            else:  # Scheduled
                                st.markdown("#### 🩺 Start Consultation")
                                
                                with st.form(f"consultation_{appt['appointment_id']}"):
                                    symptoms = st.text_area("🤒 Symptoms & Chief Complaints", 
                                                           placeholder="Patient presents with...")
                                    diagnosis = st.text_area("🔬 Clinical Diagnosis",
                                                            placeholder="Based on examination...")
                                    
                                    st.markdown("##### 💊 Prescription")
                                    med_col1, med_col2, med_col3 = st.columns(3)
                                    medication = med_col1.text_input("Medication Name")
                                    dosage = med_col2.text_input("Dosage")
                                    duration = med_col3.text_input("Duration")
                                    
                                    notes = st.text_area("📝 Additional Notes", placeholder="Any special instructions...")
                                    
                                    submit = st.form_submit_button("✅ Complete Visit", use_container_width=True, type="primary")
                                    
                                    if submit:
                                        if not diagnosis:
                                            st.error("⚠️ Diagnosis is required to complete the visit.")
                                        else:
                                            # 1. Create Consultation Record
                                            cons_query = """
                                                INSERT INTO Consultations (appointment_id, symptoms, diagnosis, notes)
                                                VALUES (%s, %s, %s, %s)
                                            """
                                            cons_id = run_query(cons_query, (appt['appointment_id'], symptoms, diagnosis, notes))
                                            
                                            # 2. Create Prescription if provided
                                            if medication and cons_id:
                                                pres_query = """
                                                    INSERT INTO Prescriptions (consultation_id, medication_name, dosage, duration)
                                                    VALUES (%s, %s, %s, %s)
                                                """
                                                run_query(pres_query, (cons_id, medication, dosage, duration))
                                            
                                            # 3. Update Appointment Status
                                            update_query = "UPDATE Appointments SET status = 'Completed' WHERE appointment_id = %s"
                                            run_query(update_query, (appt['appointment_id'],))
                                            
                                            # 4. Create Invoice
                                            invoice_query = """
                                                INSERT INTO Invoices (appointment_id, amount, payment_method)
                                                VALUES (%s, %s, 'Pending')
                                            """
                                            run_query(invoice_query, (appt['appointment_id'], consultation_fee))
                                            
                                            st.success("✅ Visit completed and invoice generated!")
                                            st.rerun()
            else:
                st.info("📭 No appointments scheduled for today.")
        else:
            st.error("⚠️ Could not find your doctor profile. Please contact the administrator.")
    else:
        st.error("⚠️ Invalid user name format. Please contact the administrator.")

# ==========================================
# 10. PAGE: PATIENTS
# ==========================================
elif selected == "Patients":
    st.title("👥 Patient Management")
    
    # Registration Form
    with st.expander("➕ Register New Patient", expanded=False):
        with st.form("patient_registration", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("First Name *")
                dob = st.date_input("Date of Birth", min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today())
                phone = st.text_input("Phone Number *")
            
            with col2:
                last_name = st.text_input("Last Name *")
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                address = st.text_area("Address")
            
            submitted = st.form_submit_button("Register Patient", use_container_width=True, type="primary")
            
            if submitted:
                if first_name and last_name and phone:
                    query = """
                        INSERT INTO Patients (first_name, last_name, date_of_birth, gender, phone, address)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    result = run_query(query, (first_name, last_name, dob, gender, phone, address))
                    if result:
                        st.success(f"✅ Patient '{first_name} {last_name}' registered successfully!")
                        st.rerun()
                else:
                    st.error("⚠️ Please fill in all required fields (marked with *)")
    
    # Search and Display
    st.markdown("### 📋 Patient Records")
    search = st.text_input("🔍 Search", placeholder="Search by name or phone...")
    
    query = """
        SELECT patient_id as ID, first_name as 'First Name', last_name as 'Last Name',
               phone as Phone, gender as Gender, date_of_birth as 'DOB'
        FROM Patients
    """
    params = None
    
    if search:
        query += " WHERE first_name LIKE %s OR last_name LIKE %s OR phone LIKE %s"
        search_term = f"%{search}%"
        params = (search_term, search_term, search_term)
    
    query += " ORDER BY patient_id DESC"
    
    patients = load_data(query, params)
    st.dataframe(patients, use_container_width=True, hide_index=True)

# ==========================================
# 11. PAGE: DOCTORS (Admin Only)
# ==========================================
elif selected == "Doctors":
    if role != "Admin":
        st.error("⛔ Access Denied: Admin privileges required")
        st.stop()
    
    st.title("👨‍⚕️ Medical Staff Directory")
    
    # Add Doctor Form
    with st.expander("➕ Add New Doctor", expanded=False):
        # Get specialties
        specialties = get_cached_data("SELECT speciality_id, speciality_name FROM Specialists")
        specialty_map = dict(zip(specialties['speciality_name'], specialties['speciality_id'])) if not specialties.empty else {}
        
        with st.form("add_doctor", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("First Name *")
                specialty = st.selectbox("Specialty *", list(specialty_map.keys()) if specialty_map else [])
                email = st.text_input("Email")
            
            with col2:
                last_name = st.text_input("Last Name *")
                phone = st.text_input("Phone")
                fee = st.number_input("Consultation Fee ($)", min_value=0.0, step=10.0)
            
            submitted = st.form_submit_button("Add Doctor", use_container_width=True, type="primary")
            
            if submitted:
                if first_name and last_name and specialty:
                    query = """
                        INSERT INTO Doctors (first_name, last_name, specialty_id, phone, email, consultation_fee)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    result = run_query(query, (first_name, last_name, specialty_map.get(specialty), phone, email, fee))
                    if result:
                        st.success(f"✅ Dr. {first_name} {last_name} added successfully!")
                        st.cache_data.clear()
                        st.rerun()
                else:
                    st.error("⚠️ Please fill in all required fields")
    
    # Display Doctors
    st.markdown("### 📋 Current Medical Staff")
    doctors = load_data("""
        SELECT d.doctor_id as ID, 
               CONCAT(d.first_name, ' ', d.last_name) as 'Doctor Name',
               s.speciality_name as Specialty,
               d.phone as Phone,
               d.email as Email,
               CONCAT('$', FORMAT(d.consultation_fee, 2)) as 'Fee'
        FROM Doctors d
        JOIN Specialists s ON d.specialty_id = s.speciality_id
        ORDER BY d.doctor_id
    """)
    st.dataframe(doctors, use_container_width=True, hide_index=True)

# ==========================================
# 12. PAGE: APPOINTMENTS
# ==========================================
elif selected == "Appointments":
    st.title("📅 Appointment Scheduler")
    
    # Booking Form
    with st.expander("📝 Book New Appointment", expanded=True):
        # Load dropdowns
        patients = load_data("SELECT patient_id, CONCAT(first_name, ' ', last_name) as name FROM Patients ORDER BY first_name")
        doctors = load_data("SELECT doctor_id, CONCAT(first_name, ' ', last_name) as name FROM Doctors ORDER BY first_name")
        
        patient_map = dict(zip(patients['name'], patients['patient_id'])) if not patients.empty else {}
        doctor_map = dict(zip(doctors['name'], doctors['doctor_id'])) if not doctors.empty else {}
        
        if not patient_map:
            st.warning("⚠️ No patients found. Please register a patient first.")
        elif not doctor_map:
            st.warning("⚠️ No doctors found. Please add a doctor first.")
        else:
            with st.form("book_appointment"):
                col1, col2 = st.columns(2)
                
                with col1:
                    selected_patient = st.selectbox("Patient *", list(patient_map.keys()))
                    appt_date = st.date_input("Date *", min_value=datetime.date.today())
                
                with col2:
                    selected_doctor = st.selectbox("Doctor *", list(doctor_map.keys()))
                    appt_time = st.time_input("Time *")
                
                submitted = st.form_submit_button("Book Appointment", use_container_width=True, type="primary")
                
                if submitted:
                    patient_id = patient_map[selected_patient]
                    doctor_id = doctor_map[selected_doctor]
                    
                    # Check for double booking
                    conflict_query = """
                        SELECT COUNT(*) as count 
                        FROM Appointments 
                        WHERE doctor_id = %s 
                        AND appointment_date = %s 
                        AND appointment_time = %s 
                        AND status != 'Cancelled'
                    """
                    conflicts = load_data(conflict_query, (doctor_id, appt_date, str(appt_time)))
                    
                    if conflicts.iloc[0]['count'] > 0:
                        st.error(f"⚠️ Dr. {selected_doctor} is not available at {appt_time} on {appt_date}. Please choose a different time.")
                    else:
                        insert_query = """
                            INSERT INTO Appointments (patient_id, doctor_id, appointment_date, appointment_time, status)
                            VALUES (%s, %s, %s, %s, 'Scheduled')
                        """
                        result = run_query(insert_query, (patient_id, doctor_id, appt_date, str(appt_time)))
                        if result:
                            st.success("✅ Appointment booked successfully!")
                            st.rerun()
    
    st.divider()
    
    # Appointments List
    st.markdown("### 📋 Upcoming Appointments")
    appointments = load_data("""
        SELECT 
            a.appointment_date as Date,
            a.appointment_time as Time,
            CONCAT(p.first_name, ' ', p.last_name) as Patient,
            CONCAT(d.first_name, ' ', d.last_name) as Doctor,
            a.status as Status
        FROM Appointments a
        JOIN Patients p ON a.patient_id = p.patient_id
        JOIN Doctors d ON a.doctor_id = d.doctor_id
        ORDER BY a.appointment_date DESC, a.appointment_time DESC
        LIMIT 100
    """)
    st.dataframe(appointments, use_container_width=True, hide_index=True)

# ==========================================
# 13. PAGE: USERS (Admin Only)
# ==========================================
elif selected == "Users":
    if role != "Admin":
        st.error("⛔ Access Denied: Admin privileges required")
        st.stop()
    
    st.title("⚙️ User Management")
    
    # Add User Form
    with st.form("add_user"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Username *")
            full_name = st.text_input("Full Name *")
        
        with col2:
            password = st.text_input("Password *", type="password")
            user_role = st.selectbox("Role *", ["Admin", "Doctor", "Secretary"])
        
        submitted = st.form_submit_button("Create User", use_container_width=True, type="primary")
        
        if submitted:
            if username and password and full_name:
                # Check if username exists
                existing = load_data("SELECT COUNT(*) as count FROM Users WHERE username = %s", (username,))
                if existing.iloc[0]['count'] > 0:
                    st.error("⚠️ Username already exists. Please choose a different username.")
                else:
                    password_hash = hash_password(password)
                    query = """
                        INSERT INTO Users (username, password_hash, full_name, role)
                        VALUES (%s, %s, %s, %s)
                    """
                    result = run_query(query, (username, password_hash, full_name, user_role))
                    if result:
                        st.success(f"✅ User '{username}' created successfully!")
                        st.rerun()
            else:
                st.error("⚠️ Please fill in all required fields")
    
    st.divider()
    
    # Users List
    st.markdown("### 📋 System Users")
    users = load_data("""
        SELECT user_id as ID, username as Username, full_name as 'Full Name', 
               role as Role, created_at as 'Created At'
        FROM Users
        ORDER BY created_at DESC
    """)
    st.dataframe(users, use_container_width=True, hide_index=True)
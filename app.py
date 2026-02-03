import streamlit as st
import mysql.connector
import pandas as pd
import datetime
import hashlib
import plotly.express as px
from streamlit_option_menu import option_menu

# ==========================================
# 1. Configuration & Global State
# ==========================================
st.set_page_config(page_title="Clinic Pro System", page_icon="🏥", layout="wide")

# Initialize Session State
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'page_selection' not in st.session_state:
    st.session_state['page_selection'] = 0 # Index of the selected page

# Custom CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border-left: 5px solid #3498db;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .stButton>button { border-radius: 20px; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. Database & Caching
# ==========================================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '7efnawinn591911',
    'database': 'ClinicDB'
}

@st.cache_resource
def get_db_connection():
    """Persistent Database Connection"""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        st.error(f"❌ Database Connection Error: {err}")
        return None

def run_query(query, params=None):
    """Execute Write Operations (Insert, Update, Delete)"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.Error as err:
            st.error(f"Query Error: {err}")
        finally:
            cursor.close()
    return None

def load_data(query, params=None):
    """Fetch Live Data (No Caching for consistency)"""
    conn = get_db_connection()
    if conn:
        return pd.read_sql(query, conn, params=params)
    return pd.DataFrame()

@st.cache_data(ttl=600)
def get_dropdown_data(table, id_col, name_col):
    """Cached Data for Dropdowns (Refreshes every 10 mins)"""
    conn = get_db_connection()
    if conn:
        query = f"SELECT {id_col}, {name_col} FROM {table}"
        return pd.read_sql(query, conn)
    return pd.DataFrame()

# ==========================================
# 3. Authentication
# ==========================================
def login_user(username, password):
    pwd_hash = hashlib.sha256(str.encode(password)).hexdigest()
    df = load_data("SELECT * FROM Users WHERE username = %s AND password_hash = %s", (username, pwd_hash))
    return df.iloc[0] if not df.empty else None

if not st.session_state['logged_in']:
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<h1 style='text-align: center;'>🔐 Clinic Login</h1>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Login", use_container_width=True):
                user = login_user(u, p)
                if user is not None:
                    st.session_state['logged_in'] = True
                    st.session_state['user_role'] = user['role']
                    st.session_state['username'] = user['full_name']
                    st.rerun()
                else:
                    st.error("Invalid Credentials")
    st.stop()

# ==========================================
# 4. Navigation & Layout
# ==========================================
role = st.session_state['user_role']

# Role-Based Menu
if role == 'Admin':
    menu_options = ["Dashboard", "Patients", "Doctors", "Appointments", "Users"]
    menu_icons = ["speedometer2", "people-fill", "hospital-fill", "calendar-check-fill", "gear-fill"]
elif role == 'Doctor':
    menu_options = ["Appointments", "Patients"]
    menu_icons = ["calendar-check-fill", "people-fill"]
else: # Secretary
    menu_options = ["Appointments", "Patients"]
    menu_icons = ["calendar-check-fill", "people-fill"]

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063176.png", width=60)
    st.write(f"User: **{st.session_state['username']}** ({role})")
    
    # Navigation
    selected = option_menu(
        menu_title=None,
        options=menu_options,
        icons=menu_icons,
        default_index=st.session_state.get('page_selection', 0),
        key='main_menu', # Key helps persist state
        styles={
            "container": {"background-color": "#2c3e50"},
            "icon": {"color": "white", "font-size": "18px"},
            "nav-link": {"color": "white", "--hover-color": "#34495e"},
            "nav-link-selected": {"background-color": "#1abc9c"},
        }
    )
    
    st.markdown("---")
    if st.button("Log Out"):
        st.session_state['logged_in'] = False
        st.rerun()

# Update session state index (Optional for strict syncing)
if selected in menu_options:
    st.session_state['page_selection'] = menu_options.index(selected)

# ==========================================
# 5. Page Implementations
# ==========================================

# --- DASHBOARD ---
if selected == "Dashboard":
    if role != "Admin":
        st.error("Access Denied")
    else:
        st.title("📊 Financial & Operational Decision Support")
        
        # 1. Filters
        with st.expander("🔎 Analysis Filters", expanded=True):
            f1, f2 = st.columns(2)
            today = datetime.date.today()
            start_date = f1.date_input("Start Date", today.replace(day=1)) # Default to 1st of month
            end_date = f2.date_input("End Date", today)
            
            # Fetch Doctor List for Filter
            docs = load_data("SELECT doctor_id, CONCAT(first_name, ' ', last_name) as name FROM Doctors")
            doc_options = dict(zip(docs['name'], docs['doctor_id'])) if not docs.empty else {}
            selected_docs = f1.multiselect("Filter by Doctor", options=list(doc_options.keys()))

        # 2. Fetch Raw Data (One Big Query) and Filter
        # Note: In real production, handle large datasets with LIMIT or pre-aggregation
        raw_query = """
        SELECT 
            a.appointment_id, a.appointment_date, a.status,
            d.doctor_id, CONCAT(d.first_name, ' ', d.last_name) as doctor_name,
            p.patient_id, p.gender,
            i.amount
        FROM Appointments a
        JOIN Doctors d ON a.doctor_id = d.doctor_id
        JOIN Patients p ON a.patient_id = p.patient_id
        LEFT JOIN Invoices i ON a.appointment_id = i.appointment_id
        WHERE a.appointment_date BETWEEN %s AND %s
        """
        df_raw = load_data(raw_query, (start_date, end_date))
        
        # Apply Doctor Filter in Pandas
        if selected_docs and not df_raw.empty:
             selected_ids = [doc_options[d] for d in selected_docs]
             df_raw = df_raw[df_raw['doctor_id'].isin(selected_ids)]
             
        if df_raw.empty:
            st.warning("No data found for the selected period/filters.")
        else:
            # 3. KPI Calculations
            total_rev = df_raw['amount'].sum()
            total_appts = len(df_raw)
            # Proxy for 'New Patients': Count unique patients seen in this period (Active Patients)
            active_patients = df_raw['patient_id'].nunique() 
            cancelled_pct = (len(df_raw[df_raw['status'] == 'Cancelled']) / total_appts * 100) if total_appts > 0 else 0
            
            # KPI Row
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("💰 Total Revenue", f"${total_rev:,.2f}")
            k2.metric("📅 Appointments", total_appts)
            k3.metric("👥 Active Patients", active_patients)
            k4.metric("🚫 Cancellation Rate", f"{cancelled_pct:.1f}%")
            
            st.markdown("---")
            
            # 4. Visual Insights (Row 1)
            r1c1, r1c2 = st.columns(2)
            
            with r1c1:
                st.subheader("Revenue Trend")
                # Group by Date
                daily_rev = df_raw.groupby('appointment_date')['amount'].sum().reset_index()
                fig_trend = px.line(daily_rev, x='appointment_date', y='amount', 
                                    markers=True, title="Daily Revenue",
                                    color_discrete_sequence=['#2ecc71'])
                st.plotly_chart(fig_trend, use_container_width=True)
                
            with r1c2:
                st.subheader("Appointment Status")
                status_counts = df_raw['status'].value_counts().reset_index()
                status_counts.columns = ['status', 'count']
                fig_status = px.pie(status_counts, values='count', names='status', hole=0.4, 
                                    title="Operational Efficiency",
                                    color_discrete_sequence=px.colors.sequential.Blues_r)
                st.plotly_chart(fig_status, use_container_width=True)
                
            # 5. Visual Insights (Row 2)
            r2c1, r2c2 = st.columns(2)
            
            with r2c1:
                st.subheader("Top Doctors by Revenue")
                doc_perf = df_raw.groupby('doctor_name')['amount'].sum().reset_index().sort_values('amount', ascending=True).tail(5)
                fig_doc = px.bar(doc_perf, x='amount', y='doctor_name', orientation='h', 
                                 title="Revenue Leaders", text_auto='.2s',
                                 color='amount', color_continuous_scale='Blues')
                st.plotly_chart(fig_doc, use_container_width=True)
                
            with r2c2:
                st.subheader("Patient Demographics")
                # Group by Gender
                gender_counts = df_raw['gender'].value_counts().reset_index()
                gender_counts.columns = ['gender', 'count']
                fig_gen = px.bar(gender_counts, x='gender', y='count', title="Patients by Gender",
                                 color='gender', color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_gen, use_container_width=True)

# --- PATIENTS ---
elif selected == "Patients":
    st.title("👥 Patient Management")
    
    # Form Wrapper
    with st.expander("➕ Register Patient"):
        with st.form("add_patient"):
            c1,c2 = st.columns(2)
            fn = c1.text_input("First Name")
            ln = c2.text_input("Last Name")
            dob = c1.date_input("DOB", min_value=datetime.date(1900,1,1))
            gen = c2.selectbox("Gender", ["Male", "Female", "Other"])
            ph = c1.text_input("Phone")
            addr = c2.text_area("Address")
            
            if st.form_submit_button("Save Record", use_container_width=True):
                if fn and ph:
                    run_query("INSERT INTO Patients (first_name, last_name, date_of_birth, gender, phone, address) VALUES (%s,%s,%s,%s,%s,%s)", 
                              (fn, ln, dob, gen, ph, addr))
                    st.success("Patient Added!")
                    st.cache_data.clear() # Invalidate cache if we had patient list cached (loaded dynamically here though)
                    st.rerun()
                else:
                    st.warning("Name and Phone required.")

    # Search & Table
    search = st.text_input("🔍 Search", placeholder="Name or Phone...")
    q = "SELECT patient_id, first_name, last_name, phone, gender, date_of_birth FROM Patients"
    p = None
    if search:
        q += " WHERE first_name LIKE %s OR last_name LIKE %s OR phone LIKE %s"
        wc = f"%{search}%"
        p = (wc,wc,wc)
    
    df = load_data(q, p)
    st.dataframe(df, use_container_width=True, hide_index=True)

# --- DOCTORS ---
elif selected == "Doctors":
    if role != "Admin":
        st.error("Admin Only")
    else:
        st.title("👨‍⚕️ Medical Staff")
        
        with st.expander("➕ Add Doctor"):
            # Cached Dropdown
            s_df = get_dropdown_data("Specialists", "speciality_id", "speciality_name")
            s_map = dict(zip(s_df['speciality_name'], s_df['speciality_id']))
            
            with st.form("add_doctor"):
                c1,c2 = st.columns(2)
                fn = c1.text_input("First Name")
                ln = c2.text_input("Last Name")
                sp = c1.selectbox("Specialty", list(s_map.keys()) if not s_df.empty else [])
                ph = c2.text_input("Phone")
                em = c1.text_input("Email")
                fee = c2.number_input("Fee", min_value=0.0)
                
                if st.form_submit_button("Save Doctor", use_container_width=True):
                    run_query("INSERT INTO Doctors (first_name, last_name, specialty_id, phone, email, consultation_fee) VALUES (%s,%s,%s,%s,%s,%s)", 
                              (fn, ln, s_map.get(sp), ph, em, fee))
                    st.success("Doctor Added!")
                    st.rerun()
        
        df = load_data("SELECT d.first_name, d.last_name, s.speciality_name, d.phone FROM Doctors d JOIN Specialists s ON d.specialty_id = s.speciality_id")
        st.dataframe(df, use_container_width=True, hide_index=True)

# --- APPOINTMENTS ---
elif selected == "Appointments":
    st.title("📅 Scheduler")
    
    with st.expander("📅 Book Appointment", expanded=True):
        # Cached Dropdowns for Form
        p_df = load_data("SELECT patient_id, CONCAT(first_name, ' ', last_name) as name FROM Patients") # Not cached due to frequent updates
        d_df = get_dropdown_data("Doctors", "doctor_id", "first_name") # Partially cached, maybe safer to load fresh or ttl short
        
        # For Doctor Display Name, we need a join usually, but let's stick to simple first name for dropdown or better query
        # Let's use a custom live query for doctors to get full naming properly
        d_df_live = load_data("SELECT doctor_id, CONCAT(first_name, ' ', last_name) as name FROM Doctors")
        
        if not p_df.empty and not d_df_live.empty:
            p_map = dict(zip(p_df['name'], p_df['patient_id']))
            d_map = dict(zip(d_df_live['name'], d_df_live['doctor_id']))
            
            with st.form("book_appt"):
                c1,c2 = st.columns(2)
                sel_p = c1.selectbox("Patient", list(p_map.keys()))
                sel_d = c2.selectbox("Doctor", list(d_map.keys()))
                dt = c1.date_input("Date", min_value=datetime.date.today())
                tm = c2.time_input("Time")
                sts = st.selectbox("Status", ["Scheduled", "Completed", "Cancelled"])
                
                if st.form_submit_button("Confirm Booking", use_container_width=True):
                    pid = p_map[sel_p]
                    did = d_map[sel_d]
                    
                    # Double Booking Logic
                    chk = load_data("SELECT COUNT(*) as c FROM Appointments WHERE doctor_id=%s AND appointment_date=%s AND appointment_time=%s AND status!='Cancelled'", 
                                    (did, dt, str(tm)))
                    
                    if chk['c'][0] > 0:
                        st.error("⚠️ Slot Unavailable!")
                    else:
                        run_query("INSERT INTO Appointments (patient_id, doctor_id, appointment_date, appointment_time, status) VALUES (%s,%s,%s,%s,%s)", 
                                  (pid, did, dt, str(tm), sts))
                        st.success("Booking Confirmed!")
                        st.rerun()

    st.divider()
    df = load_data("""
        SELECT a.appointment_date, a.appointment_time, CONCAT(p.first_name, ' ', p.last_name) as Patient, 
        CONCAT(d.first_name, ' ', d.last_name) as Doctor, a.status 
        FROM Appointments a JOIN Patients p ON a.patient_id=p.patient_id JOIN Doctors d ON a.doctor_id=d.doctor_id 
        ORDER BY a.appointment_date DESC
    """)
    st.dataframe(df, use_container_width=True, hide_index=True)

# --- USERS ---
elif selected == "Users":
    if role != "Admin":
         st.error("Admin Only")
    else:
        st.title("⚙️ User Management")
        with st.form("add_user"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            n = st.text_input("Full Name")
            r = st.selectbox("Role", ["Admin", "Doctor", "Secretary"])
            if st.form_submit_button("Create User"):
                if u and p:
                    ph = hashlib.sha256(str.encode(p)).hexdigest()
                    run_query("INSERT INTO Users (username, password_hash, full_name, role) VALUES (%s,%s,%s,%s)", (u, ph, n, r))
                    st.success("User Created")
                    st.rerun()
        
        st.dataframe(load_data("SELECT username, full_name, role, created_at FROM Users"), use_container_width=True)
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hashlib
from datetime import datetime
import os

# Configure Streamlit for wide mode
st.set_page_config(
    page_title="Healthcare Performance Management System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database initialization
def init_database():
    """Initialize SQLite database"""
    conn = sqlite3.connect('healthcare_performance.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            department TEXT,
            full_name TEXT
        )
    ''')
    
    # Create performance_data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS performance_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            woreda_name TEXT NOT NULL,
            department TEXT NOT NULL,
            entered_by TEXT NOT NULL,
            medical_service REAL DEFAULT 0,
            rmh REAL DEFAULT 0,
            pharmacy_logistic REAL DEFAULT 0,
            ultrasound REAL DEFAULT 0,
            apts REAL DEFAULT 0,
            community_pharmacy REAL DEFAULT 0,
            dm_test REAL DEFAULT 0,
            epi REAL DEFAULT 0,
            child_health REAL DEFAULT 0,
            tb_leprosy REAL DEFAULT 0,
            phem REAL DEFAULT 0,
            cbhi REAL DEFAULT 0,
            finance REAL DEFAULT 0,
            plan REAL DEFAULT 0,
            wt REAL DEFAULT 0,
            full_emr REAL DEFAULT 0,
            epi_modernization REAL DEFAULT 0,
            zero_dose REAL DEFAULT 0,
            multi_sectoral REAL DEFAULT 0,
            cash_program REAL DEFAULT 0,
            hygiene_sanitation REAL DEFAULT 0,
            hiv_sti REAL DEFAULT 0,
            total_score REAL DEFAULT 0,
            percentage_score REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database
init_database()

# Authentication functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username, password):
    conn = sqlite3.connect('healthcare_performance.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT role, department FROM users WHERE username = ? AND password = ?', 
                  (username, hash_password(password)))
    result = cursor.fetchone()
    conn.close()
    return result

# Get woredas list
def get_woredas():
    return [
        'Debre Sina Health Center',
        'Armania Health Center',
        'Agamber Health Center',
        'Mezezo Health Center'
    ]

# Calculate scores
def calculate_scores(data):
    # Medical & Pharmacy (37.5 pts)
    medical_pharmacy = (
        data.get('medical_service', 0) +
        data.get('rmh', 0) +
        data.get('pharmacy_logistic', 0) +
        data.get('ultrasound', 0) +
        data.get('apts', 0) +
        data.get('community_pharmacy', 0) +
        data.get('dm_test', 0)
    )
    
    # Prevention & Disease (20 pts)
    prevention_disease = (
        data.get('epi', 0) +
        data.get('child_health', 0) +
        data.get('tb_leprosy', 0) +
        data.get('phem', 0)
    )
    
    # Admin & Finance (25 pts)
    admin_finance = (
        data.get('cbhi', 0) +
        data.get('finance', 0) +
        data.get('plan', 0) +
        data.get('wt', 0)
    )
    
    # Innovation & Quality (22.5 pts)
    innovation_quality = (
        data.get('full_emr', 0) +
        data.get('epi_modernization', 0) +
        data.get('zero_dose', 0) +
        data.get('multi_sectoral', 0) +
        data.get('cash_program', 0) +
        data.get('hygiene_sanitation', 0) +
        data.get('hiv_sti', 0)
    )
    
    total_score = medical_pharmacy + prevention_disease + admin_finance + innovation_quality
    percentage_score = (total_score / 105) * 100
    
    return total_score, percentage_score

# Login page
def login_page():
    st.title("🏥 Healthcare Performance Management System")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("🔐 User Login")
        
        # Use form to ensure proper input handling
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "Username", 
                placeholder="Enter your username",
                key="username_field",
                help="Enter your department username"
            )
            password = st.text_input(
                "Password", 
                type="password", 
                placeholder="Enter your password",
                key="password_field",
                help="Enter your password"
            )
            
            submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted:
                # Validate inputs
                if not username or not password:
                    st.error("⚠️ Please enter both username and password")
                    return
                
                # Trim whitespace
                username = username.strip()
                password = password.strip()
                
                # Authenticate user
                result = verify_user(username, password)
                if result:
                    st.session_state.authenticated = True
                    st.session_state.role = result[0]
                    st.session_state.department = result[1]
                    st.session_state.username = username
                    st.success(f"Welcome {username}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")

# Simple dashboard
def simple_dashboard():
    st.title(f"📊 {st.session_state.role} Dashboard")
    st.markdown(f"**Logged in as:** {st.session_state.username}")
    
    if st.session_state.role == "Department Head":
        st.success("🏥 Department Head Interface")
        st.info("Data entry functionality available in full version")
    elif st.session_state.role == "Admin":
        st.success("👨‍💼 Admin Dashboard")
        st.info("View rankings and analytics in full version")
    elif st.session_state.role == "Super Admin":
        st.success("👑 Super Admin Dashboard")
        st.info("Full system management in full version")
    
    st.markdown("---")
    st.subheader("📋 System Information")
    st.write(f"**Total Health Centers:** {len(get_woredas())}")
    st.write("**Total Possible Score:** 105 points")
    st.write("**Status:** System Running Successfully")
    
    if st.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Main application
def main():
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Check authentication
    if not st.session_state.authenticated:
        login_page()
    else:
        simple_dashboard()

if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hashlib
from datetime import datetime

# Custom CSS to hide the Streamlit logo, header, and footer
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# Custom CSS to hide Streamlit header, footer, and main menu branding
st.markdown("""
<style>
/* Hide Streamlit header */
[data-testid="stHeader"] {
    display: none;
}

/* Hide Streamlit footer */
[data-testid="stFooter"] {
    display: none;
}

/* Hide main menu branding */
[data-testid="stSidebarHeader"] {
    display: none;
}

/* Hide "Made with Streamlit" branding */
[data-testid="stSidebarContent"] > div:first-child {
    display: none;
}

/* Hide Streamlit's default sidebar elements */
[data-testid="stSidebarNav"] {
    display: none;
}

/* Custom sidebar header */
.custom-sidebar-header {
    background-color: #1f77b4;
    color: white;
    padding: 20px;
    text-align: center;
    border-radius: 10px;
    margin-bottom: 20px;
}

/* Hide any remaining Streamlit branding */
.streamlit-container .main .block-container {
    padding-top: 2rem;
}

/* Remove Streamlit's default footer spacing */
.main .block-container {
    padding-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

# Configure Streamlit for wide mode
st.set_page_config(
    page_title="Healthcare Performance Management System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database initialization
def init_database():
    """Initialize SQLite database with proper error handling for cloud deployment"""
    try:
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
        
        # Clear any existing users to avoid conflicts
        cursor.execute('DELETE FROM users')
        
        # Insert default users with correct credentials
        default_users = [
            ('admin', hash_password('admin@2018'), 'Admin', 'Administration', 'System Administrator'),
            ('superadmin', hash_password('super@2024'), 'Super Admin', 'Administration', 'Super Administrator'),
            ('epi', hash_password('EPI@2024'), 'Department Head', 'EPI', 'EPI Department'),
            ('tb', hash_password('TB@2024'), 'Department Head', 'TB & Leprosy', 'TB & Leprosy Department'),
            ('child health', hash_password('Child Health@2024'), 'Department Head', 'Child Health', 'Child Health Department'),
            ('phem', hash_password('PHEM@2024'), 'Department Head', 'PHEM', 'PHEM Department'),
            ('cbhi', hash_password('CBHI@2024'), 'Department Head', 'CBHI', 'CBHI Department'),
            ('finance', hash_password('Finance@2024'), 'Department Head', 'Finance', 'Finance Department'),
            ('plan', hash_password('Plan@2024'), 'Department Head', 'Plan', 'Plan Department'),
            ('wt', hash_password('WT@2024'), 'Department Head', 'WT', 'WT Department'),
            ('medical', hash_password('Medical@2024'), 'Department Head', 'Medical Service', 'Medical Service Department'),
            ('rmh', hash_password('RMH@2024'), 'Department Head', 'RMH', 'RMH Department'),
            ('pharmacy', hash_password('Pharmacy@2024'), 'Department Head', 'Pharmacy & Logistic', 'Pharmacy & Logistic Department'),
            ('ultrasound', hash_password('Ultrasound@2024'), 'Department Head', 'Ultrasound', 'Ultrasound Department'),
            ('apts', hash_password('APTS@2024'), 'Department Head', 'APTS', 'APTS Department'),
            ('community_pharmacy', hash_password('CommunityPharmacy@2024'), 'Department Head', 'Community Pharmacy', 'Community Pharmacy Department'),
            ('dm_test', hash_password('DMTest@2024'), 'Department Head', 'DM Test', 'DM Test Department'),
            ('full_emr', hash_password('FullEMR@2024'), 'Department Head', 'Full EMR', 'Full EMR Department'),
            ('epi_modernization', hash_password('EPIModernization@2024'), 'Department Head', 'EPI Modernization', 'EPI Modernization Department'),
            ('zero_dose', hash_password('ZeroDose@2024'), 'Department Head', 'Zero Dose', 'Zero Dose Department'),
            ('multi_sectoral', hash_password('MultiSectoral@2024'), 'Department Head', 'Multi-Sectoral', 'Multi-Sectoral Department'),
            ('cash_program', hash_password('CashProgram@2024'), 'Department Head', 'Cash Program', 'Cash Program Department'),
            ('hygiene', hash_password('Hygiene@2024'), 'Department Head', 'Hygiene & Sanitation', 'Hygiene & Sanitation Department'),
            ('hiv_sti', hash_password('HIVSTI@2024'), 'Department Head', 'HIV/STI', 'HIV/STI Department')
        ]
        
        for user in default_users:
            cursor.execute('''
                INSERT INTO users (username, password, role, department, full_name)
                VALUES (?, ?, ?, ?, ?)
            ''', user)
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Database initialization error: {str(e)}")
        return False

# Authentication functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username, password):
    try:
        conn = sqlite3.connect('healthcare_performance.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('SELECT role, department FROM users WHERE username = ? AND password = ?', 
                      (username, hash_password(password)))
        result = cursor.fetchone()
        conn.close()
        return result
    except:
        return None

# Get woredas list
def get_woredas():
    return [
        'Angolela Tara Woreda', 'Ankober Woreda', 'Antsokia Gemiza Woreda', 'Asagirt Woreda',
        'Bassona Worana', 'Berehet Woreda', 'Efratana Gidim Woreda', 'Ensaro Woreda',
        'Gishe Woreda', 'Hagere Mariam Woreda', 'Kewot Woreda', 'Menz Gera Midir Woreda',
        'Menz Keya Gebreal Woreda', 'Menz Lalo Midir Woreda', 'Menz Mama Midir Woreda',
        'Merhabete Woreda', 'Mida Woremo Woreda', 'Minjar Shenkora Woreda', 'Mojana Wodera Woreda',
        'Mortena Jiru Woreda', 'Saya Deberna Wayu Woreda', 'Shewarobit Town', 'Taremaber Woreda'
    ]

# Calculate scores
def calculate_scores(data):
    # Medical & Pharmacy (40 pts)
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
    
    # Innovation & Quality (25 pts)
    innovation_quality = (
        data.get('full_emr', 0) +  # 5 pts
        data.get('epi_modernization', 0) +  # 2.5 pts
        data.get('zero_dose', 0) +  # 2.5 pts
        data.get('multi_sectoral', 0) +  # 2.5 pts
        data.get('cash_program', 0) +  # 2.5 pts
        data.get('hygiene_sanitation', 0) +  # 5 pts
        data.get('hiv_sti', 0)  # 5 pts
    )
    
    # Total points: 40 + 20 + 25 + 25 = 110 points
    # Medical & Pharmacy breakdown: 15 + 10 + 5 + 2.5 + 2.5 + 2.5 + 2.5 = 40 pts ✅
    # Innovation & Quality breakdown: 5 + 2.5 + 2.5 + 2.5 + 2.5 + 5 + 5 = 25 pts ✅
    
    total_score = medical_pharmacy + prevention_disease + admin_finance + innovation_quality
    percentage_score = (total_score / 110) * 100
    
    return total_score, percentage_score

# Save performance data
def save_performance_data(woreda_name, department, data, entered_by):
    try:
        conn = sqlite3.connect('healthcare_performance.db', check_same_thread=False)
        cursor = conn.cursor()
        
        total_score, percentage_score = calculate_scores(data)
        
        # Check if record exists
        cursor.execute('''
            SELECT id FROM performance_data 
            WHERE woreda_name = ? AND department = ? AND entered_by = ?
        ''', (woreda_name, department, entered_by))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing record
            cursor.execute('''
                UPDATE performance_data SET
                    medical_service = ?, rmh = ?, pharmacy_logistic = ?, ultrasound = ?, 
                    apts = ?, community_pharmacy = ?, dm_test = ?, epi = ?, child_health = ?, 
                    tb_leprosy = ?, phem = ?, cbhi = ?, finance = ?, plan = ?, wt = ?, 
                    full_emr = ?, epi_modernization = ?, zero_dose = ?, multi_sectoral = ?, 
                    cash_program = ?, hygiene_sanitation = ?, hiv_sti = ?, total_score = ?, 
                    percentage_score = ?, updated_at = CURRENT_TIMESTAMP
                WHERE woreda_name = ? AND department = ? AND entered_by = ?
            ''', (
                data.get('medical_service', 0), data.get('rmh', 0), data.get('pharmacy_logistic', 0),
                data.get('ultrasound', 0), data.get('apts', 0), data.get('community_pharmacy', 0),
                data.get('dm_test', 0), data.get('epi', 0), data.get('child_health', 0),
                data.get('tb_leprosy', 0), data.get('phem', 0), data.get('cbhi', 0),
                data.get('finance', 0), data.get('plan', 0), data.get('wt', 0),
                data.get('full_emr', 0), data.get('epi_modernization', 0), data.get('zero_dose', 0),
                data.get('multi_sectoral', 0), data.get('cash_program', 0), data.get('hygiene_sanitation', 0),
                data.get('hiv_sti', 0), total_score, percentage_score, woreda_name, department, entered_by
            ))
        else:
            # Insert new record
            cursor.execute('''
                INSERT INTO performance_data (
                    woreda_name, department, entered_by, medical_service, rmh, pharmacy_logistic, 
                    ultrasound, apts, community_pharmacy, dm_test, epi, child_health, tb_leprosy, 
                    phem, cbhi, finance, plan, wt, full_emr, epi_modernization, zero_dose, 
                    multi_sectoral, cash_program, hygiene_sanitation, hiv_sti, total_score, percentage_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                woreda_name, department, entered_by, data.get('medical_service', 0), data.get('rmh', 0),
                data.get('pharmacy_logistic', 0), data.get('ultrasound', 0), data.get('apts', 0),
                data.get('community_pharmacy', 0), data.get('dm_test', 0), data.get('epi', 0),
                data.get('child_health', 0), data.get('tb_leprosy', 0), data.get('phem', 0),
                data.get('cbhi', 0), data.get('finance', 0), data.get('plan', 0), data.get('wt', 0),
                data.get('full_emr', 0), data.get('epi_modernization', 0), data.get('zero_dose', 0),
                data.get('multi_sectoral', 0), data.get('cash_program', 0), data.get('hygiene_sanitation', 0),
                data.get('hiv_sti', 0), total_score, percentage_score
            ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")
        return False

# Get performance data
def get_performance_data():
    try:
        conn = sqlite3.connect('healthcare_performance.db', check_same_thread=False)
        query = '''
            SELECT woreda_name, SUM(total_score) as total_score, 
                   AVG(percentage_score) as percentage_score
            FROM performance_data 
            GROUP BY woreda_name
            ORDER BY total_score DESC
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

# Department Head Interface
def department_head_interface(department, username):
    st.title(f"📊 {department} Data Entry")
    st.markdown(f"**Department:** {department}")
    st.markdown(f"**Logged in as:** {username}")
    
    # Column info for department
    column_info = {
        'EPI': {'epi': {'label': 'EPI', 'max': 5}},
        'TB & Leprosy': {'tb_leprosy': {'label': 'TB & Leprosy', 'max': 5}},
        'Child Health': {'child_health': {'label': 'Child Health', 'max': 5}},
        'PHEM': {'phem': {'label': 'PHEM', 'max': 5}},
        'CBHI': {'cbhi': {'label': 'CBHI', 'max': 10}},
        'Finance': {'finance': {'label': 'Finance', 'max': 5}},
        'Plan': {'plan': {'label': 'Plan', 'max': 5}},
        'WT': {'wt': {'label': 'WT', 'max': 5}},
        'Medical Service': {'medical_service': {'label': 'Medical Service', 'max': 15}},
        'RMH': {'rmh': {'label': 'RMH', 'max': 10}},
        'Pharmacy & Logistic': {'pharmacy_logistic': {'label': 'Pharmacy & Logistic', 'max': 5}},
        'Ultrasound': {'ultrasound': {'label': 'Ultrasound', 'max': 2.5}},
        'APTS': {'apts': {'label': 'APTS', 'max': 2.5}},
        'Community Pharmacy': {'community_pharmacy': {'label': 'Community Pharmacy', 'max': 2.5}},
        'DM Test': {'dm_test': {'label': 'DM Test', 'max': 2.5}},
        'Full EMR': {'full_emr': {'label': 'Full EMR', 'max': 5}},
        'EPI Modernization': {'epi_modernization': {'label': 'EPI Modernization', 'max': 2.5}},  # Reduced from 5 to 2.5
        'Zero Dose': {'zero_dose': {'label': 'Zero Dose', 'max': 2.5}},  # Reduced from 5 to 2.5
        'Multi-Sectoral': {'multi_sectoral': {'label': 'Multi-Sectoral', 'max': 2.5}},
        'Cash Program': {'cash_program': {'label': 'Cash Program', 'max': 2.5}},
        'Hygiene & Sanitation': {'hygiene_sanitation': {'label': 'Hygiene & Sanitation', 'max': 5}},  # Increased from 2.5 to 5
        'HIV/STI': {'hiv_sti': {'label': 'HIV/STI', 'max': 5}}  # Increased from 2.5 to 5
    }
    
    if department in column_info:
        col_info = column_info[department]
        for key, info in col_info.items():
            st.subheader(f"📝 Enter {info['label']} Data")
            
            woredas = get_woredas()
            input_data = {}
            
            for woreda in woredas:
                input_data[woreda] = st.number_input(
                    f"{woreda} (Max: {info['max']})",
                    min_value=0.0,
                    max_value=float(info['max']),
                    value=0.0,
                    step=0.1,
                    key=f"{key}_{woreda}"
                )
            
            if st.button(f"💾 Save {info['label']} Data", use_container_width=True):
                success_count = 0
                for woreda, value in input_data.items():
                    data = {key: value}
                    if save_performance_data(woreda, department, data, username):
                        success_count += 1
                
                if success_count > 0:
                    st.success(f"Saved {info['label']} data for {success_count} Woredas!")
                else:
                    st.error("Failed to save data")
            
            st.markdown("---")
    
    # Show current rankings
    st.subheader("📋 Current Rankings")
    rankings = get_performance_data()
    if not rankings.empty:
        st.dataframe(rankings, use_container_width=True)
    else:
        st.info("No performance data available yet")

# Admin Dashboard
def admin_dashboard():
    st.title("📊 Admin Dashboard")
    st.markdown(f"**Logged in as:** {st.session_state.username}")
    
    # Get performance data
    rankings = get_performance_data()
    
    if not rankings.empty:
        # KPI Cards
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_score = rankings['total_score'].mean()
            st.metric("Average Score", f"{avg_score:.1f}/110")
        with col2:
            max_score = rankings['total_score'].max()
            st.metric("Highest Score", f"{max_score:.1f}/110")
        with col3:
            total_woredas = len(rankings)
            st.metric("Total Woredas", total_woredas)
        
        # Bar Chart
        st.subheader("📈 Performance Rankings")
        fig = px.bar(rankings, x='woreda_name', y='total_score', 
                    title="Woreda Performance Rankings",
                    labels={'total_score': 'Total Score', 'woreda_name': 'Woreda Name'})
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Data Table
        st.subheader("📋 Detailed Data")
        st.dataframe(rankings, use_container_width=True)
    else:
        st.info("No performance data available. Please have department heads enter data first.")

# Super Admin Dashboard
def super_admin_dashboard():
    st.title("👑 Super Admin Dashboard")
    st.markdown(f"**Logged in as:** {st.session_state.username}")
    
    # Show admin dashboard
    admin_dashboard()
    
    # Additional super admin features
    st.markdown("---")
    st.subheader("🔧 System Management")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("📊 User Management")
        st.write("Feature to manage users will be available")
    
    with col2:
        st.info("🗃️ Database Management")
        st.write("Feature to manage database will be available")

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

# Main application
def main():
    # Initialize database
    if not init_database():
        st.error("Failed to initialize database. Please try again.")
        return
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Check authentication
    if not st.session_state.authenticated:
        login_page()
    else:
        # Sidebar with navigation and logout
        with st.sidebar:
            st.title("🏥 Navigation")
            
            # User info
            st.markdown(f"**Logged in as:** {st.session_state.username}")
            st.markdown(f"**Role:** {st.session_state.role}")
            st.markdown("---")
            
            # Logout button
            if st.button("🚪 Logout", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        
        # Main content based on role
        if st.session_state.role == "Department Head":
            department_head_interface(st.session_state.department, st.session_state.username)
        elif st.session_state.role == "Admin":
            admin_dashboard()
        elif st.session_state.role == "Super Admin":
            super_admin_dashboard()
        else:
            st.error("Unknown role. Please contact administrator.")
    
    # Add footer with enhanced visibility
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 30px 0; background-color: #f8f9fa; border-top: 3px solid #1f77b4; margin-top: 40px;">
        <p style="color: #1f77b4; font-size: 18px; font-weight: bold; margin: 10px 0;">© 2026 All Rights Reserved</p>
        <p style="color: #333; font-size: 16px; margin: 8px 0;">Developed by <strong style="color: #1f77b4;">Abe_Technology</strong></p>
        <p style="color: #333; font-size: 16px; margin: 8px 0;">Contact via Telegram: <a href="https://t.me/AI_Technology" target="_blank" style="color: #1f77b4; text-decoration: none; font-weight: bold;">@AI_Technology</a></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

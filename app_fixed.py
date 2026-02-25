import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hashlib
from datetime import datetime
import os

# Custom CSS to hide ALL Streamlit branding elements
hide_st_style = """
<style>
/* Hide main menu hamburger icon */
#MainMenu {visibility: hidden;}

/* Hide footer */
footer {visibility: hidden;}

/* Hide header */
header {visibility: hidden;}

/* Hide Streamlit's default header */
[data-testid="stHeader"] {
    display: none;
}

/* Hide Streamlit's default footer */
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

/* Hide any remaining Streamlit branding */
.stDeployButton {
    display: none;
}

/* Hide the Streamlit toolbar */
[data-testid="stToolbar"] {
    display: none;
}

/* Remove Streamlit's default footer spacing */
.main .block-container {
    padding-bottom: 2rem;
}

/* Custom sidebar header styling */
.custom-sidebar-header {
    background-color: #1f77b4;
    color: white;
    padding: 20px;
    text-align: center;
    border-radius: 10px;
    margin-bottom: 20px;
}

/* Hide any remaining Streamlit branding text */
.streamlit-container .main .block-container {
    padding-top: 2rem;
}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

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
        # Use absolute path for better cloud compatibility
        db_path = os.path.join(os.getcwd(), 'healthcare_performance.db')
        conn = sqlite3.connect(db_path, check_same_thread=False)
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
        
        # Check if users exist, if not, insert them
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            # Insert default users with exact department mappings
            default_users = [
                ('admin', hash_password('admin@2018'), 'Admin', 'All', 'System Administrator'),
                ('superadmin', hash_password('super@2024'), 'Super Admin', 'All', 'Super Administrator'),
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
            
            st.success("Database initialized with default users!")
        else:
            st.info(f"Database already has {user_count} users configured.")
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Database initialization error: {str(e)}")
        return False

# Authentication functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_login(username, password):
    """Verify login credentials with debug information"""
    try:
        db_path = os.path.join(os.getcwd(), 'healthcare_performance.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Hash the password
        hashed_password = hash_password(password)
        
        # Check user credentials
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password))
        user = cursor.fetchone()
        
        # Debug: Show all users (remove in production)
        cursor.execute('SELECT username, role FROM users')
        all_users = cursor.fetchall()
        
        conn.close()
        
        if user:
            return {
                'success': True,
                'user': {
                    'id': user[0],
                    'username': user[1],
                    'role': user[3],
                    'department': user[4],
                    'full_name': user[5]
                },
                'debug': f"Login successful. Found {len(all_users)} users in database."
            }
        else:
            return {
                'success': False,
                'debug': f"Login failed. Found {len(all_users)} users in database. Tried username: '{username}'"
            }
    except Exception as e:
        return {
            'success': False,
            'debug': f"Database error: {str(e)}"
        }

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

# Department Head Interface - COMPLETE REWRITE
def department_head_interface(department, username):
    st.title(f"📊 {department} Data Entry")
    st.markdown(f"**Department:** {department}")
    st.markdown(f"**Logged in as:** {username}")
    
    # Store user department in session state for filtering
    st.session_state.user_dept = department
    
    # Define department to column mappings
    DEPARTMENT_COLUMNS = {
        'EPI': ['epi'],
        'TB & Leprosy': ['tb_leprosy'],
        'Child Health': ['child_health'],
        'PHEM': ['phem'],
        'CBHI': ['cbhi'],
        'Finance': ['finance'],
        'Plan': ['plan'],
        'WT': ['wt'],
        'Medical Service': ['medical_service'],
        'RMH': ['rmh'],
        'Pharmacy & Logistic': ['pharmacy_logistic'],
        'Ultrasound': ['ultrasound'],
        'APTS': ['apts'],
        'Community Pharmacy': ['community_pharmacy'],
        'DM Test': ['dm_test'],
        'Full EMR': ['full_emr'],
        'EPI Modernization': ['epi_modernization'],
        'Zero Dose': ['zero_dose'],
        'Multi-Sectoral': ['multi_sectoral'],
        'Cash Program': ['cash_program'],
        'Hygiene & Sanitation': ['hygiene_sanitation'],
        'HIV/STI': ['hiv_sti']
    }
    
    # Define column display info
    COLUMN_INFO = {
        'epi': {'label': 'EPI', 'max': 5},
        'tb_leprosy': {'label': 'TB & Leprosy', 'max': 5},
        'child_health': {'label': 'Child Health', 'max': 5},
        'phem': {'label': 'PHEM', 'max': 5},
        'cbhi': {'label': 'CBHI', 'max': 10},
        'finance': {'label': 'Finance', 'max': 5},
        'plan': {'label': 'Plan', 'max': 5},
        'wt': {'label': 'WT', 'max': 5},
        'medical_service': {'label': 'Medical Service', 'max': 15},
        'rmh': {'label': 'RMH', 'max': 10},
        'pharmacy_logistic': {'label': 'Pharmacy & Logistic', 'max': 5},
        'ultrasound': {'label': 'Ultrasound', 'max': 2.5},
        'apts': {'label': 'APTS', 'max': 2.5},
        'community_pharmacy': {'label': 'Community Pharmacy', 'max': 2.5},
        'dm_test': {'label': 'DM Test', 'max': 2.5},
        'full_emr': {'label': 'Full EMR', 'max': 5},
        'epi_modernization': {'label': 'EPI Modernization', 'max': 2.5},
        'zero_dose': {'label': 'Zero Dose', 'max': 2.5},
        'multi_sectoral': {'label': 'Multi-Sectoral', 'max': 2.5},
        'cash_program': {'label': 'Cash Program', 'max': 2.5},
        'hygiene_sanitation': {'label': 'Hygiene & Sanitation', 'max': 5},
        'hiv_sti': {'label': 'HIV/STI', 'max': 5}
    }
    
    # Get columns for this user's department
    user_columns = DEPARTMENT_COLUMNS.get(department, [])
    
    if not user_columns:
        st.error(f"❌ No valid data elements assigned to this user. Department '{department}' not found.")
        st.warning("Available departments:")
        for dept in DEPARTMENT_COLUMNS.keys():
            st.write(f"- {dept}")
        return
    
    st.success(f"✅ Found {len(user_columns)} data elements for {department}")
    
    # Dynamic form generation for each column
    for column_name in user_columns:
        column_info = COLUMN_INFO.get(column_name)
        if not column_info:
            continue
            
        st.subheader(f"📝 Enter {column_info['label']} Data")
        
        # Get all woredas
        woredas = get_woredas()
        input_data = {}
        
        # Create dynamic number inputs for all woredas
        cols = st.columns(3)  # 3-column layout
        for i, woreda in enumerate(woredas):
            col = cols[i % 3]
            with col:
                input_data[woreda] = st.number_input(
                    f"{woreda} (Max: {column_info['max']})",
                    min_value=0.0,
                    max_value=float(column_info['max']),
                    value=0.0,
                    step=0.1,
                    key=f"{column_name}_{woreda}_{username}"  # Unique key per user
                )
        
        # Save button for this column
        if st.button(f"💾 Save {column_info['label']} Data", use_container_width=True, key=f"save_{column_name}"):
            success_count = 0
            error_count = 0
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, (woreda, value) in enumerate(input_data.items()):
                try:
                    data = {column_name: value}
                    if save_performance_data(woreda, department, data, username):
                        success_count += 1
                    else:
                        error_count += 1
                except Exception as e:
                    error_count += 1
                    st.error(f"Error saving {woreda}: {str(e)}")
                
                # Update progress
                progress = (i + 1) / len(input_data)
                progress_bar.progress(progress)
                status_text.text(f"Saving... {i + 1}/{len(input_data)} Woredas")
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Show results
            if success_count > 0:
                st.success(f"✅ Successfully saved {column_info['label']} data for {success_count} Woredas!")
            if error_count > 0:
                st.error(f"❌ Failed to save data for {error_count} Woredas")
        
        st.markdown("---")
    
    # Show current data summary
    show_department_data_summary(department)

def show_department_data_summary(department):
    """Show current data summary for the department"""
    st.subheader("📋 Current Data Summary")
    
    try:
        conn = sqlite3.connect('healthcare_performance.db', check_same_thread=False)
        
        # Get department-specific data
        query = '''
            SELECT woreda_name, total_score, percentage_score, entered_by, updated_at
            FROM performance_data 
            WHERE department = ? 
            ORDER BY woreda_name
        '''
        df = pd.read_sql_query(query, conn, params=(department,))
        
        if not df.empty:
            st.info(f"No data available for {department} yet.")
        else:
            st.write(f"📊 **{department} Data Summary:**")
            st.dataframe(df, use_container_width=True)
            
            # Show statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_score = df['total_score'].mean()
                st.metric("Average Score", f"{avg_score:.2f}")
            with col2:
                max_score = df['total_score'].max()
                st.metric("Highest Score", f"{max_score:.2f}")
            with col3:
                total_entries = len(df)
                st.metric("Total Entries", total_entries)
        
        conn.close()
    except Exception as e:
        st.error(f"Error loading data summary: {str(e)}")

# Admin Dashboard - VIEW ONLY
def admin_dashboard():
    st.title("📊 Admin Dashboard (View Only)")
    st.markdown(f"**Logged in as:** {st.session_state.username}")
    st.info("👁️ Admin users can view all data but cannot modify. Contact Super Admin for data entry.")
    
    # Show current rankings
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
        
        # Detailed Ranking Table - FIXED HTML DISPLAY
        st.subheader("📋 Detailed Ranking Table")
        
        # Create ranking table with conditional formatting
        ranking_data = []
        for rank, row in enumerate(rankings.itertuples(), 1):
            percentage = row.percentage_score
            
            # Apply conditional formatting with 3-color scheme
            if percentage >= 80:
                percentage_class = "high-percentage"
                percentage_display = f"{percentage:.1f}% 🟢"
            elif percentage >= 50:
                percentage_class = "medium-percentage"
                percentage_display = f"{percentage:.1f}% 🟡"
            else:
                percentage_class = "low-percentage"
                percentage_display = f"{percentage:.1f}% 🔴"
            
            ranking_data.append({
                'Rank': rank,
                'Woreda Name': row.woreda_name,
                'Total Score (Out of 110)': f"{row.total_score:.1f}",
                'Final Percentage (%)': percentage_display,
                'Color Class': percentage_class
            })
        
        ranking_df = pd.DataFrame(ranking_data)
        
        # Apply custom CSS for conditional formatting
        st.markdown("""
        <style>
        .high-percentage {
            background-color: #d4edda !important;
            color: #155724 !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            padding: 8px !important;
            text-align: center !important;
            border: 2px solid #28a745 !important;
        }
        .medium-percentage {
            background-color: #fff3cd !important;
            color: #856404 !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            padding: 8px !important;
            text-align: center !important;
            border: 2px solid #ffc107 !important;
        }
        .low-percentage {
            background-color: #f8d7da !important;
            color: #721c24 !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            padding: 8px !important;
            text-align: center !important;
            border: 2px solid #dc3545 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Display ranking table with color coding using HTML - PROPERLY FIXED
        ranking_html = """
        <table style="width: 100%; border-collapse: separate; border-spacing: 0; font-size: 18px; font-weight: bold; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <thead>
                <tr style="background: linear-gradient(135deg, #1f77b4, #1565c0); color: white; font-weight: 900;">
                    <th style="padding: 15px; border: none; text-align: center; font-size: 20px;">Rank</th>
                    <th style="padding: 15px; border: none; text-align: left; font-size: 20px;">Woreda Name</th>
                    <th style="padding: 15px; border: none; text-align: center; font-size: 20px;">Total Score (Out of 110)</th>
                    <th style="padding: 15px; border: none; text-align: center; font-size: 20px;">Final Percentage (%)</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for _, row in ranking_df.iterrows():
            percentage = float(row['Final Percentage (%)'].replace('%', '').replace('**', '').replace('🟢', '').replace('🟡', '').replace('🔴', '').strip())
            
            # Apply color coding with better thresholds
            if percentage >= 80:
                bg_color = '#d4edda'
                text_color = '#155724'
                emoji = '🟢'
                border_color = '#28a745'
            elif percentage >= 50:
                bg_color = '#fff3cd'
                text_color = '#856404'
                emoji = '🟡'
                border_color = '#ffc107'
            else:
                bg_color = '#f8d7da'
                text_color = '#721c24'
                emoji = '🔴'
                border_color = '#dc3545'
            
            ranking_html += f"""
                <tr style="background-color: {'white' if _ % 2 == 0 else '#f8f9fa'}; transition: all 0.3s ease;">
                    <td style="padding: 12px; border: none; font-weight: bold; text-align: center; color: #2c3e50;">{row['Rank']}</td>
                    <td style="padding: 12px; border: none; font-weight: bold; text-align: left; color: #2c3e50;">{row['Woreda Name']}</td>
                    <td style="padding: 12px; border: none; font-weight: bold; text-align: center; background: linear-gradient(135deg, #e3f2fd, #bbdefb); color: #1565c0; font-size: 20px; border: 2px solid #1f77b4; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">{row['Total Score (Out of 110)']}</td>
                    <td style="padding: 12px; border: none; font-weight: 900; text-align: center; background: {bg_color}; color: {text_color}; font-size: 20px; border: 2px solid {border_color}; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); position: relative; overflow: hidden;">
                        <span style="position: relative; z-index: 2;">{percentage:.1f}% {emoji}</span>
                        <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);"></div>
                    </td>
                </tr>
            """
        
        ranking_html += """
            </tbody>
        </table>
        
        <style>
        table tr:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        </style>
        """
        
        # PROPERLY RENDER HTML TABLE
        st.markdown(ranking_html, unsafe_allow_html=True)
    else:
        st.info("No performance data available. Please have department heads enter data first.")

# Super Admin Dashboard - FULL ACCESS
def super_admin_dashboard():
    st.title("👑 Super Admin Dashboard")
    st.markdown(f"**Logged in as:** {st.session_state.username}")
    st.success("🔓 Super Admin: Full access to all departments and data entry")
    
    # Department selector for Super Admin
    all_departments = list(DEPARTMENT_COLUMNS.keys()) if 'DEPARTMENT_COLUMNS' in globals() else [
        'EPI', 'TB & Leprosy', 'Child Health', 'PHEM', 'CBHI', 'Finance', 'Plan', 'WT',
        'Medical Service', 'RMH', 'Pharmacy & Logistic', 'Ultrasound', 'APTS', 'Community Pharmacy',
        'DM Test', 'Full EMR', 'EPI Modernization', 'Zero Dose', 'Multi-Sectoral',
        'Cash Program', 'Hygiene & Sanitation', 'HIV/STI'
    ]
    
    selected_dept = st.selectbox("🏥 Select Department to Manage:", all_departments)
    
    if selected_dept:
        st.info(f"Managing: {selected_dept}")
        # Call department head interface with Super Admin access
        department_head_interface(selected_dept, st.session_state.username)
    
    # Show admin dashboard
    admin_dashboard()

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
        
        # Detailed Ranking Table
        st.subheader("📋 Detailed Ranking Table")
        
        # Create ranking table with conditional formatting
        ranking_data = []
        for rank, row in enumerate(rankings.itertuples(), 1):
            percentage = row.percentage_score
            
            # Apply conditional formatting with 3-color scheme
            if percentage >= 80:
                percentage_class = "high-percentage"
                percentage_display = f"{percentage:.1f}% 🟢"
            elif percentage >= 50:
                percentage_class = "medium-percentage"
                percentage_display = f"{percentage:.1f}% 🟡"
            else:
                percentage_class = "low-percentage"
                percentage_display = f"{percentage:.1f}% 🔴"
            
            ranking_data.append({
                'Rank': rank,
                'Woreda Name': row.woreda_name,
                'Total Score (Out of 110)': f"{row.total_score:.1f}",
                'Final Percentage (%)': percentage_display,
                'Color Class': percentage_class
            })
        
        ranking_df = pd.DataFrame(ranking_data)
        
        # Apply custom CSS for conditional formatting
        st.markdown("""
        <style>
        .high-percentage {
            background-color: #d4edda !important;
            color: #155724 !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            padding: 8px !important;
            text-align: center !important;
            border: 2px solid #28a745 !important;
        }
        .medium-percentage {
            background-color: #fff3cd !important;
            color: #856404 !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            padding: 8px !important;
            text-align: center !important;
            border: 2px solid #ffc107 !important;
        }
        .low-percentage {
            background-color: #f8d7da !important;
            color: #721c24 !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            padding: 8px !important;
            text-align: center !important;
            border: 2px solid #dc3545 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Display ranking table with color coding using HTML
        ranking_html = """
        <table style="width: 100%; border-collapse: separate; border-spacing: 0; font-size: 18px; font-weight: bold; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <thead>
                <tr style="background: linear-gradient(135deg, #1f77b4, #1565c0); color: white; font-weight: 900;">
                    <th style="padding: 15px; border: none; text-align: center; font-size: 20px;">Rank</th>
                    <th style="padding: 15px; border: none; text-align: left; font-size: 20px;">Woreda Name</th>
                    <th style="padding: 15px; border: none; text-align: center; font-size: 20px;">Total Score (Out of 110)</th>
                    <th style="padding: 15px; border: none; text-align: center; font-size: 20px;">Final Percentage (%)</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for _, row in ranking_df.iterrows():
            percentage = float(row['Final Percentage (%)'].replace('%', '').replace('**', '').replace('🟢', '').replace('🟡', '').replace('🔴', '').strip())
            
            # Apply color coding with better thresholds
            if percentage >= 80:
                bg_color = '#d4edda'
                text_color = '#155724'
                emoji = '🟢'
                border_color = '#28a745'
            elif percentage >= 50:
                bg_color = '#fff3cd'
                text_color = '#856404'
                emoji = '🟡'
                border_color = '#ffc107'
            else:
                bg_color = '#f8d7da'
                text_color = '#721c24'
                emoji = '🔴'
                border_color = '#dc3545'
            
            ranking_html += f"""
                <tr style="background-color: {'white' if _ % 2 == 0 else '#f8f9fa'}; transition: all 0.3s ease;">
                    <td style="padding: 12px; border: none; font-weight: bold; text-align: center; color: #2c3e50;">{row['Rank']}</td>
                    <td style="padding: 12px; border: none; font-weight: bold; text-align: left; color: #2c3e50;">{row['Woreda Name']}</td>
                    <td style="padding: 12px; border: none; font-weight: bold; text-align: center; background: linear-gradient(135deg, #e3f2fd, #bbdefb); color: #1565c0; font-size: 20px; border: 2px solid #1f77b4; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">{row['Total Score (Out of 110)']}</td>
                    <td style="padding: 12px; border: none; font-weight: 900; text-align: center; background: {bg_color}; color: {text_color}; font-size: 20px; border: 2px solid {border_color}; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); position: relative; overflow: hidden;">
                        <span style="position: relative; z-index: 2;">{percentage:.1f}% {emoji}</span>
                        <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);"></div>
                    </td>
                </tr>
            """
        
        ranking_html += """
            </tbody>
        </table>
        
        <style>
        table tr:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        </style>
        """
        
        st.markdown(ranking_html, unsafe_allow_html=True)
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
                
                # Authenticate user with debug information
                login_result = verify_login(username, password)
                
                if login_result['success']:
                    st.session_state.authenticated = True
                    st.session_state.role = login_result['user']['role']
                    st.session_state.department = login_result['user']['department']
                    st.session_state.username = username
                    st.success(f"Welcome {username}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
                    # Show debug information in development
                    st.info(f"Debug: {login_result['debug']}")
                    
                    # Show available users for debugging
                    try:
                        db_path = os.path.join(os.getcwd(), 'healthcare_performance.db')
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()
                        cursor.execute('SELECT username, role FROM users')
                        users = cursor.fetchall()
                        conn.close()
                        
                        if users:
                            st.write("Available users:")
                            for user in users:
                                st.write(f"- {user[0]} ({user[1]})")
                        else:
                            st.warning("No users found in database!")
                    except Exception as e:
                        st.error(f"Could not fetch users: {str(e)}")

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

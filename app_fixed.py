import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hashlib
from datetime import datetime
import os

# Ethiopian Fiscal Year Quarter Definitions
ETHIOPIAN_QUARTERS = {
    'Q1 (Hamle - Meskerem)': {
        'code': 'Q1',
        'months': 'Hamle - Meskerem',
        'description': 'Ethiopian Quarter 1: Hamle to Meskerem'
    },
    'Q2 (Tikmt - Tahsas)': {
        'code': 'Q2',
        'months': 'Tikmt - Tahsas',
        'description': 'Ethiopian Quarter 2: Tikmt to Tahsas'
    },
    'Q3 (Tir - Megabit)': {
        'code': 'Q3',
        'months': 'Tir - Megabit',
        'description': 'Ethiopian Quarter 3: Tir to Megabit'
    },
    'Q4 (Miyazia - Sene)': {
        'code': 'Q4',
        'months': 'Miyazia - Sene',
        'description': 'Ethiopian Quarter 4: Miyazia to Sene'
    }
}

def get_current_ethiopian_year():
    """Get current Ethiopian year"""
    # Ethiopian calendar is roughly 7-8 years behind Gregorian
    # Current Gregorian year 2026 = Ethiopian year 2018-2019
    # This is approximate - for exact conversion, more complex logic needed
    current_year = datetime.now().year
    ethiopian_year = current_year - 8
    return ethiopian_year

def get_current_ethiopian_quarter():
    """Get current Ethiopian quarter based on Gregorian months"""
    # This is approximate mapping - adjust based on exact Ethiopian calendar dates
    current_month = datetime.now().month
    
    # Approximate mapping (adjust as needed)
    if current_month in [9, 10, 11]:  # Sep-Nov
        return 'Q1 (Hamle - Meskerem)'
    elif current_month in [12, 1, 2]:  # Dec-Feb
        return 'Q2 (Tikmt - Tahsas)'
    elif current_month in [3, 4, 5]:  # Mar-May
        return 'Q3 (Tir - Megabit)'
    else:  # Jun-Aug
        return 'Q4 (Miyazia - Sene)'

def get_ethiopian_year_options():
    """Get list of Ethiopian years for dropdown"""
    current_year = get_current_ethiopian_year()
    return [str(year) for year in range(current_year - 2, current_year + 3)]

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
                ethiopian_year INTEGER NOT NULL,
                quarter TEXT NOT NULL,
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
        'Debre Sina Health Center',
        'Armania Health Center',
        'Agamber Health Center',
        'Mezezo Health Center'
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
def save_performance_data(woreda_name, department, data, entered_by, ethiopian_year, quarter):
    try:
        conn = sqlite3.connect('healthcare_performance.db', check_same_thread=False)
        cursor = conn.cursor()
        
        total_score, percentage_score = calculate_scores(data)
        
        # Check if record exists for this woreda, department, year, and quarter
        cursor.execute('''
            SELECT id FROM performance_data 
            WHERE woreda_name = ? AND department = ? AND ethiopian_year = ? AND quarter = ?
        ''', (woreda_name, department, ethiopian_year, quarter))
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
                WHERE woreda_name = ? AND department = ? AND ethiopian_year = ? AND quarter = ?
            ''', (
                data.get('medical_service', 0), data.get('rmh', 0), data.get('pharmacy_logistic', 0),
                data.get('ultrasound', 0), data.get('apts', 0), data.get('community_pharmacy', 0),
                data.get('dm_test', 0), data.get('epi', 0), data.get('child_health', 0),
                data.get('tb_leprosy', 0), data.get('phem', 0), data.get('cbhi', 0),
                data.get('finance', 0), data.get('plan', 0), data.get('wt', 0),
                data.get('full_emr', 0), data.get('epi_modernization', 0), data.get('zero_dose', 0),
                data.get('multi_sectoral', 0), data.get('cash_program', 0), data.get('hygiene_sanitation', 0),
                data.get('hiv_sti', 0), total_score, percentage_score,
                woreda_name, department, ethiopian_year, quarter
            ))
        else:
            # Insert new record
            cursor.execute('''
                INSERT INTO performance_data (
                    woreda_name, department, entered_by, ethiopian_year, quarter,
                    medical_service, rmh, pharmacy_logistic, ultrasound, apts, community_pharmacy, 
                    dm_test, epi, child_health, tb_leprosy, phem, cbhi, finance, plan, wt, 
                    full_emr, epi_modernization, zero_dose, multi_sectoral, cash_program, 
                    hygiene_sanitation, hiv_sti, total_score, percentage_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                woreda_name, department, entered_by, ethiopian_year, quarter,
                data.get('medical_service', 0), data.get('rmh', 0), data.get('pharmacy_logistic', 0),
                data.get('ultrasound', 0), data.get('apts', 0), data.get('community_pharmacy', 0),
                data.get('dm_test', 0), data.get('epi', 0), data.get('child_health', 0),
                data.get('tb_leprosy', 0), data.get('phem', 0), data.get('cbhi', 0),
                data.get('finance', 0), data.get('plan', 0), data.get('wt', 0),
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
def get_performance_data(ethiopian_year=None, quarter=None):
    try:
        conn = sqlite3.connect('healthcare_performance.db', check_same_thread=False)
        
        # Build query with optional filters
        base_query = '''
            SELECT woreda_name, SUM(total_score) as total_score, 
                   AVG(percentage_score) as percentage_score
            FROM performance_data 
        '''
        
        conditions = []
        params = []
        
        if ethiopian_year:
            conditions.append("ethiopian_year = ?")
            params.append(ethiopian_year)
            
        if quarter:
            conditions.append("quarter = ?")
            params.append(quarter)
        
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
        
        base_query += '''
            GROUP BY woreda_name
            ORDER BY total_score DESC
        '''
        
        df = pd.read_sql_query(base_query, conn, params=params)
        conn.close()
        df = df[df['woreda_name'].isin(get_woredas())].copy()
        return df
    except Exception as e:
        st.error(f"Error fetching performance data: {str(e)}")
        return pd.DataFrame()

# Department Head Interface - SIMPLE & CLEAN
def department_head_interface(department, username):
    st.title(f"📊 {department} Data Entry")
    st.markdown(f"**Department:** {department}")
    st.markdown(f"**Logged in as:** {username}")
    
    # Department to columns mapping
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
    
    # Column information
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
    
    # Get user columns
    user_columns = DEPARTMENT_COLUMNS.get(department, [])
    
    # Try case-insensitive match if exact fails
    if not user_columns:
        for dept_key, columns in DEPARTMENT_COLUMNS.items():
            if dept_key.lower() == department.lower():
                user_columns = columns
                break
    
    # Check if department found
    if not user_columns:
        st.error(f"Department '{department}' not found.")
        st.write("Available departments:")
        for dept in DEPARTMENT_COLUMNS.keys():
            st.write(f"- {dept}")
        return
    
    # Ethiopian Year and Quarter Selection
    st.markdown("---")
    st.subheader("📅 Select Period")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ethiopian_years = get_ethiopian_year_options()
        selected_year = st.selectbox(
            "Ethiopian Year",
            options=ethiopian_years,
            index=0
        )
    
    with col2:
        quarter_options = list(ETHIOPIAN_QUARTERS.keys())
        selected_quarter = st.selectbox(
            "Quarter",
            options=quarter_options,
            index=0
        )
    
    quarter_info = ETHIOPIAN_QUARTERS[selected_quarter]
    st.info(f"**Period:** Ethiopian Year {selected_year} - {selected_quarter}")
    
    # Data Entry Forms
    for column_name in user_columns:
        column_info = COLUMN_INFO.get(column_name)
        if not column_info:
            continue
            
        st.subheader(f"📝 {column_info['label']} Data")
        
        # Get woredas and create inputs
        woredas = get_woredas()
        input_data = {}
        
        cols = st.columns(3)
        for i, woreda in enumerate(woredas):
            col = cols[i % 3]
            with col:
                input_data[woreda] = st.number_input(
                    f"{woreda} (Max: {column_info['max']})",
                    min_value=0.0,
                    max_value=float(column_info['max']),
                    value=0.0,
                    step=0.1,
                    key=f"{column_name}_{woreda}_{username}"
                )
        
        # Save button
        if st.button(f"Save {column_info['label']} Data", use_container_width=True):
            success_count = 0
            
            for woreda, value in input_data.items():
                try:
                    data = {column_name: value}
                    if save_performance_data(woreda, department, data, username, selected_year, selected_quarter):
                        success_count += 1
                except:
                    pass
            
            if success_count > 0:
                st.success(f"Saved data for {success_count} woredas!")
            else:
                st.error("Failed to save data")
        
        st.markdown("---")

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
        df = df[df['woreda_name'].isin(get_woredas())].copy()
        
        if df.empty:
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
    st.info("View-only access to all data")
    
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
    
    # Ethiopian Fiscal Year and Quarter Filtering
    st.markdown("---")
    st.subheader("📅 Filter by Ethiopian Fiscal Year")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Ethiopian Year Selection
        ethiopian_years = get_ethiopian_year_options()
        filter_year = st.selectbox(
            "📆 Ethiopian Year",
            options=ethiopian_years,
            index=ethiopian_years.index(str(get_current_ethiopian_year())),
            key="superadmin_filter_year"
        )
    
    with col2:
        # Quarter Selection
        quarter_options = ["All"] + list(ETHIOPIAN_QUARTERS.keys())
        filter_quarter = st.selectbox(
            "📊 Quarter",
            options=quarter_options,
            index=quarter_options.index(get_current_ethiopian_quarter()),
            key="superadmin_filter_quarter"
        )
    
    # Show selected period info
    if filter_quarter != "All":
        quarter_info = ETHIOPIAN_QUARTERS[filter_quarter]
        st.info(f"📅 **Filtering:** Ethiopian Year {filter_year} - {filter_quarter} ({quarter_info['months']})")
    else:
        st.info(f"📅 **Filtering:** All Quarters for Ethiopian Year {filter_year}")
    
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
    
    # Show filtered admin dashboard
    st.markdown("---")
    st.subheader("📊 Performance Dashboard")
    
    # Get filtered performance data
    quarter_param = None if filter_quarter == "All" else filter_quarter
    rankings = get_performance_data(ethiopian_year=filter_year, quarter=quarter_param)
    
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
        st.info("No performance data available for the selected period. Please have department heads enter data first.")

# Admin Dashboard
def admin_dashboard():
    st.title("📊 Admin Dashboard (View Only)")
    st.markdown(f"**Logged in as:** {st.session_state.username}")
    st.info("View-only access to all data")
    
    # Ethiopian Fiscal Year and Quarter Filtering
    st.markdown("---")
    st.subheader("📅 Filter by Ethiopian Fiscal Year")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Ethiopian Year Selection
        ethiopian_years = get_ethiopian_year_options()
        filter_year = st.selectbox(
            "📆 Ethiopian Year",
            options=ethiopian_years,
            index=ethiopian_years.index(str(get_current_ethiopian_year())),
            key="admin_filter_year"
        )
    
    with col2:
        # Quarter Selection
        quarter_options = ["All"] + list(ETHIOPIAN_QUARTERS.keys())
        filter_quarter = st.selectbox(
            "📊 Quarter",
            options=quarter_options,
            index=quarter_options.index(get_current_ethiopian_quarter()),
            key="admin_filter_quarter"
        )
    
    # Show selected period info
    if filter_quarter != "All":
        quarter_info = ETHIOPIAN_QUARTERS[filter_quarter]
        st.info(f"📅 **Filtering:** Ethiopian Year {filter_year} - {filter_quarter} ({quarter_info['months']})")
    else:
        st.info(f"📅 **Filtering:** All Quarters for Ethiopian Year {filter_year}")
    
    # Get filtered performance data
    quarter_param = None if filter_quarter == "All" else filter_quarter
    rankings = get_performance_data(ethiopian_year=filter_year, quarter=quarter_param)
    
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

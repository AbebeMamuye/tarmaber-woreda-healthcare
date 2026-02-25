import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit.components.v1 import html
import hashlib
from datetime import datetime

# Configure Streamlit for wide mode
st.set_page_config(
    page_title="Healthcare Performance Management System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database initialization
def init_db():
    conn = sqlite3.connect('healthcare_performance.db')
    cursor = conn.cursor()
    
    # Users table with updated structure
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
    
    # Performance data table with user tracking
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
    
    # Add hiv_sti column if it doesn't exist (for existing databases)
    cursor.execute('PRAGMA table_info(performance_data)')
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Current database columns: {columns}")
    print(f"Number of columns: {len(columns)}")
    
    if 'hiv_sti' not in columns:
        cursor.execute('''
            ALTER TABLE performance_data ADD COLUMN hiv_sti REAL DEFAULT 0
        ''')
        print("Added hiv_sti column")
    
    # Remove old hiv and sti columns if they exist
    if 'hiv' in columns:
        try:
            cursor.execute('ALTER TABLE performance_data DROP COLUMN hiv')
            print("Dropped hiv column")
        except:
            print("Could not drop hiv column (SQLite limitation)")
    if 'sti' in columns:
        try:
            cursor.execute('ALTER TABLE performance_data DROP COLUMN sti')
            print("Dropped sti column")
        except:
            print("Could not drop sti column (SQLite limitation)")
    
    # Get final column count
    cursor.execute('PRAGMA table_info(performance_data)')
    final_columns = [row[1] for row in cursor.fetchall()]
    print(f"Final database columns: {final_columns}")
    print(f"Final number of columns: {len(final_columns)}")
    
    # Insert default users if not exists
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        # Updated users with new credentials and data elements
        users_data = [
            ("admin", "4421", "Admin", "ADMIN", ""),
            ("epi", "7634", "Department Head", "EPI", "epi,epi_modernization,zero_dose"),
            ("pharmacy", "6777", "Department Head", "Pharmacy", "community_pharmacy,apts,pharmacy_logistic"),
            ("cash", "9096", "Department Head", "Cash", "cash_program,hygiene_sanitation"),
            ("plan", "8993", "Department Head", "Plan", "full_emr,plan"),
            ("finace", "1977", "Department Head", "Finance", "cbhi,finance"),
            ("medical_service", "1900", "Department Head", "Medical Service", "medical_service"),
            ("rmh", "8878", "Department Head", "RMH", "rmh"),
            ("ultrasound", "1245", "Department Head", "Ultrasound", "ultrasound"),
            ("dm_test", "8767", "Department Head", "DM Test", "dm_test"),
            ("child_health", "3455", "Department Head", "Child Health", "child_health"),
            ("tb_leprosy", "5443", "Department Head", "TB & Leprosy", "tb_leprosy"),
            ("phem", "1877", "Department Head", "PHEM", "phem"),
            ("multi_sectoral", "1833", "Department Head", "Multi-Sectoral", "multi_sectoral"),
            ("wt", "4511", "Department Head", "WT", "wt"),
            ("hiv", "6641", "Department Head", "HIV/STI", "hiv_sti"),
            ("superadmin", "1800", "Super Admin", "SUPER ADMIN", "")
        ]
        
        for username, password, role, full_name, data_elements in users_data:
            cursor.execute('''
                INSERT INTO users (username, password, role, department, full_name)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password, role, full_name, data_elements))
    else:
        # Check if HIV user exists and create if not
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'hiv'")
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO users (username, password, role, department, full_name)
                VALUES (?, ?, ?, ?, ?)
            ''', ("hiv", "6641", "Department Head", "HIV/STI", "hiv_sti"))
            print("HIV user created manually")
    
    conn.commit()
    conn.close()

# Authentication functions
def verify_user(username, password):
    conn = sqlite3.connect('healthcare_performance.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT role, department, full_name FROM users 
        WHERE username = ? AND password = ?
    ''', (username, password))
    result = cursor.fetchone()
    conn.close()
    
    # Debug: Print authentication attempt
    print(f"Login attempt: username='{username}', password='{password}'")
    print(f"Database result: {result}")
    
    return result

def save_performance_data(woreda_name, department, data, entered_by):
    """Save performance data to database"""
    conn = sqlite3.connect('healthcare_performance.db')
    cursor = conn.cursor()
    
    # Get actual database schema
    cursor.execute('PRAGMA table_info(performance_data)')
    db_columns = [row[1] for row in cursor.fetchall()]
    print(f"Database columns: {db_columns}")
    print(f"Number of columns: {len(db_columns)}")
    
    total_score, percentage_score = calculate_scores(data)
    
    # Check if record exists
    cursor.execute('''
        SELECT id FROM performance_data 
        WHERE woreda_name = ? AND department = ? AND entered_by = ?
    ''', (woreda_name, department, entered_by))
    existing = cursor.fetchone()
    
    # Build dynamic SQL based on actual database columns
    data_columns = [col for col in db_columns if col not in ['id', 'woreda_name', 'department', 'entered_by', 'total_score', 'percentage_score', 'created_at', 'updated_at']]
    print(f"Data columns: {data_columns}")
    
    if existing:
        # Dynamic UPDATE
        set_clauses = [f"{col} = ?" for col in data_columns]
        set_clauses.extend(["total_score = ?", "percentage_score = ?", "updated_at = CURRENT_TIMESTAMP"])
        
        update_sql = f'''
            UPDATE performance_data SET 
                {', '.join(set_clauses)}
            WHERE woreda_name = ? AND department = ? AND entered_by = ?
        '''
        
        # Build values list
        values = [data.get(col, 0) for col in data_columns]
        values.extend([total_score, percentage_score, woreda_name, department, entered_by])
        
        print(f"UPDATE SQL: {update_sql}")
        print(f"Values count: {len(values)}")
        
        cursor.execute(update_sql, values)
    else:
        # Dynamic INSERT
        all_columns = ['woreda_name', 'department', 'entered_by'] + data_columns + ['total_score', 'percentage_score']
        placeholders = ['?' for _ in all_columns]
        
        insert_sql = f'''
            INSERT INTO performance_data ({', '.join(all_columns)})
            VALUES ({', '.join(placeholders)})
        '''
        
        # Build values list
        values = [woreda_name, department, entered_by]
        values.extend([data.get(col, 0) for col in data_columns])
        values.extend([total_score, percentage_score])
        
        print(f"INSERT SQL: {insert_sql}")
        print(f"Values count: {len(values)}")
        
        cursor.execute(insert_sql, values)
    
    conn.commit()
    conn.close()

# Data management functions
def get_woredas():
    return [
        'Angolela Tara Woreda', 'Ankober Woreda', 'Antsokia Gemiza Woreda', 'Asagirt Woreda',
        'Bassona Worana', 'Berehet Woreda', 'Efratana Gidim Woreda', 'Ensaro Woreda',
        'Gishe Woreda', 'Hagere Mariam Woreda', 'Kewot Woreda', 'Menz Gera Midir Woreda',
        'Menz Keya Gebreal Woreda', 'Menz Lalo Midir Woreda', 'Menz Mama Midir Woreda',
        'Merhabete Woreda', 'Mida Woremo Woreda', 'Minjar Shenkora Woreda', 'Mojana Wodera Woreda',
        'Mortena Jiru Woreda', 'Saya Deberna Wayu Woreda', 'Shewarobit Town', 'Taremaber Woreda'
    ]

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
    
    # Innovation & Quality (32.5 pts)
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

def get_performance_data():
    conn = sqlite3.connect('healthcare_performance.db')
    df = pd.read_sql_query('SELECT * FROM performance_data', conn)
    conn.close()
    return df

def get_woreda_rankings():
    conn = sqlite3.connect('healthcare_performance.db')
    query = '''
        SELECT 
            woreda_name,
            SUM(total_score) as total_score,
            SUM(percentage_score) as percentage_score
        FROM performance_data 
        GROUP BY woreda_name 
        ORDER BY percentage_score DESC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    df['rank'] = range(1, len(df) + 1)
    return df

def get_woreda_detailed_data(woreda_name):
    conn = sqlite3.connect('healthcare_performance.db')
    query = '''
        SELECT * FROM performance_data WHERE woreda_name = ?
    '''
    df = pd.read_sql_query(query, conn, params=(woreda_name,))
    conn.close()
    return df

# UI Components
def login_page():
    # Add marquee at the very top
    st.markdown("""
    <style>
    .marquee {
        width: 100%;
        overflow: hidden;
        white-space: nowrap;
        box-sizing: border-box;
        background-color: #1f77b4;
        padding: 10px 0;
        margin: 0;
    }
    .marquee span {
        display: inline-block;
        padding-left: 100%;
        animation: marquee 12s linear infinite;
        font-size: 40px;
        font-weight: bold;
        color: white;
    }
    @keyframes marquee {
        0% { transform: translate(0, 0); }
        100% { transform: translate(-100%, 0); }
    }
    
    /* Fix input field styling */
    .stTextInput > div > div > input {
        background-color: white !important;
        border: 2px solid #1f77b4 !important;
        border-radius: 8px !important;
        padding: 12px !important;
        font-size: 16px !important;
        font-weight: bold !important;
        color: black !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #2e7cd6 !important;
        box-shadow: 0 0 5px rgba(31, 123, 180, 0.5) !important;
    }
    </style>
    <div class="marquee">
        <span>Healthcare Performance Management System</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Add professional header with white space
    st.markdown("""
    <div style="text-align: center; padding: 40px 0; background-color: white;">
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("🔐 Secure Login")
        st.info("Please enter your credentials to access the system")
        
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
                
                # Debug logging
                print(f"Login attempt - Username: '{username}', Password: '{password}'")
                
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
    
    # Add footer with enhanced visibility
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 30px 0; background-color: #f8f9fa; border-top: 3px solid #1f77b4; margin-top: 40px;">
        <p style="color: #1f77b4; font-size: 18px; font-weight: bold; margin: 10px 0;"> 2026 All Rights Reserved</p>
        <p style="color: #333; font-size: 16px; margin: 8px 0;">Developed by <strong style="color: #1f77b4;">Abe_Technology</strong></p>
        <p style="color: #333; font-size: 16px; margin: 8px 0;">Contact via Telegram: <strong style="color: #1f77b4;">AI_Technology</strong></p>
    </div>
    """, unsafe_allow_html=True)

def department_head_interface(department, username):
    # Add custom CSS for styling
    st.markdown("""
    <style>
    .stNumberInput > div > div > input {
        font-weight: bold;
        border: 2px solid #1f77b4;
        border-radius: 8px;
        padding: 8px;
        font-size: 16px;
    }
    .stNumberInput > label {
        font-weight: bold;
        color: #2c3e50;
        font-size: 14px;
        background-color: #f0f2f6;
        padding: 5px 10px;
        border-radius: 5px;
        border-left: 4px solid #1f77b4;
    }
    .data-section {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin-bottom: 20px;
    }
    .woreda-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        background-color: white;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .woreda-table th {
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        text-align: left;
        padding: 12px 15px;
        font-size: 16px;
    }
    .woreda-table td {
        padding: 10px 15px;
        border-bottom: 1px solid #dee2e6;
        font-size: 14px;
    }
    .woreda-table tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    .woreda-table tr:hover {
        background-color: #e3f2fd;
    }
    .woreda-name {
        font-weight: bold;
        color: #2c3e50;
        font-size: 14px;
        min-width: 250px;
    }
    .input-field {
        width: 120px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title(f"📊 {department} Data Entry")
    st.markdown(f"**Department:** {department}")
    st.markdown(f"**Logged in as:** {username}")
    
    # Get user's data elements from database
    conn = sqlite3.connect('healthcare_performance.db')
    cursor = conn.cursor()
    cursor.execute("SELECT full_name FROM users WHERE username = ?", (username,))
    user_data = cursor.fetchone()
    conn.close()
    
    # Parse data elements from full_name field
    data_elements_str = user_data[0] if user_data and user_data[0] else ""
    data_elements = data_elements_str.split(',') if data_elements_str else []
    data_elements = [elem.strip() for elem in data_elements if elem.strip()]
    
    if not data_elements:
        st.error("No data elements assigned to this user. Please contact administrator.")
        return
    
    # Create dropdown for data element selection
    column_info = {
        'epi': {'label': 'EPI', 'max': 5},
        'epi_modernization': {'label': 'EPI Modernization', 'max': 5},
        'zero_dose': {'label': 'Zero Dose', 'max': 5},
        'community_pharmacy': {'label': 'Community Pharmacy', 'max': 2.5},
        'apts': {'label': 'APTS', 'max': 2.5},
        'pharmacy_logistic': {'label': 'Pharmacy & Logistic', 'max': 5},
        'cash_program': {'label': 'Cash Program', 'max': 5},
        'hygiene_sanitation': {'label': 'Hygiene & Sanitation', 'max': 5},
        'full_emr': {'label': 'Full EMR', 'max': 5},
        'plan': {'label': 'Plan', 'max': 5},
        'cbhi': {'label': 'CBHI', 'max': 10},
        'finance': {'label': 'Finance', 'max': 5},
        'medical_service': {'label': 'Medical Service', 'max': 15},
        'rmh': {'label': 'RMH', 'max': 10},
        'ultrasound': {'label': 'Ultrasound', 'max': 2.5},
        'dm_test': {'label': 'DM Test', 'max': 2.5},
        'child_health': {'label': 'Child Health', 'max': 5},
        'tb_leprosy': {'label': 'TB & Leprosy', 'max': 5},
        'phem': {'label': 'PHEM', 'max': 5},
        'multi_sectoral': {'label': 'Multi-Sectoral', 'max': 2.5},
        'wt': {'label': 'WT', 'max': 5},
        'hiv_sti': {'label': 'HIV/STI', 'max': 5}
    }
    
    # Filter valid data elements
    valid_elements = []
    element_labels = {}
    for elem in data_elements:
        if elem in column_info:
            valid_elements.append(elem)
            element_labels[elem] = column_info[elem]['label']
    
    if not valid_elements:
        st.error("No valid data elements assigned to this user. Please contact administrator.")
        return
    
    # Dropdown for selecting data element
    selected_element = st.selectbox(
        "🎯 Select Data Element to Edit:",
        options=valid_elements,
        format_func=lambda x: element_labels.get(x, x),
        key="data_element_selector"
    )
    
    if selected_element:
        col_info = column_info[selected_element]
        
        st.markdown(f'<div class="data-section">', unsafe_allow_html=True)
        st.subheader(f"📝 Edit {col_info['label']} Data")
        
        # Get all existing data for this department
        conn = sqlite3.connect('healthcare_performance.db')
        query = '''
            SELECT woreda_name, department, entered_by,
                   medical_service, rmh, pharmacy_logistic, ultrasound, apts, community_pharmacy, dm_test,
                   epi, child_health, tb_leprosy, phem, cbhi, finance, plan, wt,
                   full_emr, epi_modernization, zero_dose, multi_sectoral, cash_program,
                   hygiene_sanitation, hiv_sti, total_score, percentage_score
            FROM performance_data 
            WHERE department = ?
            ORDER BY woreda_name
        '''
        existing_data = pd.read_sql_query(query, conn, params=(department,))
        conn.close()
        
        # Create editable table
        woredas = get_woredas()
        
        # Initialize data structure
        data_dict = {}
        for woreda in woredas:
            data_dict[woreda] = 0.0
        
        # Load existing values
        if not existing_data.empty:
            for _, row in existing_data.iterrows():
                if row['woreda_name'] in data_dict:
                    data_dict[row['woreda_name']] = row[selected_element] or 0.0
        
        # Create input fields for each woreda in table layout
        st.write(f"**Enter {col_info['label']} values for each Woreda:**")
        
        input_data = {}
        
        # Create table with embedded input fields
        st.markdown(f"""
        <style>
        .woreda-input-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .woreda-input-table th {{
            background-color: #1f77b4;
            color: white;
            font-weight: bold;
            text-align: left;
            padding: 12px 15px;
            font-size: 16px;
        }}
        .woreda-input-table td {{
            padding: 10px 15px;
            border-bottom: 1px solid #dee2e6;
            font-size: 14px;
            vertical-align: middle;
        }}
        .woreda-input-table tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        .woreda-input-table tr:hover {{
            background-color: #e3f2fd;
        }}
        .woreda-name-cell {{
            font-weight: bold;
            color: #2c3e50;
            font-size: 14px;
            min-width: 250px;
        }}
        </style>
        """, unsafe_allow_html=True)
        
        # Table header
        st.markdown(f"""
        <table class="woreda-input-table">
            <thead>
                <tr>
                    <th>🏘️ Woreda Name</th>
                    <th>{col_info['label']} Value (Max: {col_info['max']})</th>
                </tr>
            </thead>
            <tbody>
        </table>
        """, unsafe_allow_html=True)
        
        # Create rows with input fields
        for i, woreda in enumerate(woredas):
            max_value = float(col_info['max'])
            
            # Create columns for each row
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                <div style="padding: 8px 15px; border-bottom: 1px solid #dee2e6; background-color: {'#f8f9fa' if i % 2 == 1 else 'white'};">
                    <strong>🏘️ {woreda}</strong>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                input_data[woreda] = st.number_input(
                    f"Value",
                    min_value=0.0,
                    max_value=max_value,
                    value=data_dict[woreda],
                    step=0.5,
                    key=f"{woreda}_{selected_element}",
                    label_visibility="collapsed"
                )
        
        st.markdown("---")
        
        # Calculate and display sum
        total_sum = sum(input_data.values())
        st.metric(f"📊 {col_info['label']} Total", f"{total_sum:.2f}")
        
        # Save button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(f"💾 Save {col_info['label']} Data", use_container_width=True, type="primary"):
                # Save each woreda's data with explicit parameter names
                for woreda, value in input_data.items():
                    data = {selected_element: value}
                    try:
                        save_performance_data(woreda, department, data, username)
                    except Exception as e:
                        st.error(f"Error saving data for {woreda}: {str(e)}")
                        continue
                
                st.success(f"All {col_info['label']} data saved successfully!")
                st.balloons()
        
        # Display current data table
        st.markdown("---")
        st.subheader(f"📋 {col_info['label']} Data Summary")
        
        # Create summary table
        summary_data = []
        for woreda in woredas:
            summary_data.append({
                'Woreda': woreda,
                'Value': input_data[woreda],
                'Entered By': username
            })
        
        # Add total row
        summary_data.append({
            'Woreda': 'ZONAL',
            'Value': total_sum,
            'Entered By': 'System'
        })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        # Show department-specific statistics
        st.markdown("---")
        st.subheader("📈 Department Statistics")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Woredas", len(woredas))
        with col2:
            non_zero_count = sum(1 for v in input_data.values() if v > 0)
            st.metric("Woredas with Data", non_zero_count)
        with col3:
            avg_value = total_sum / len(woredas) if len(woredas) > 0 else 0
            st.metric("Average Value", f"{avg_value:.2f}")
        
        # Show other available data elements
        if len(valid_elements) > 1:
            st.markdown("---")
            st.info(f"📌 You have access to {len(valid_elements)} data elements: {', '.join([element_labels[elem] for elem in valid_elements])}")
            st.info("💡 Use the dropdown above to switch between data elements.")
        
        st.markdown('</div>', unsafe_allow_html=True)

def admin_dashboard():
    # Add marquee at the very top
    st.markdown("""
    <style>
    .marquee {
        width: 100%;
        overflow: hidden;
        white-space: nowrap;
        box-sizing: border-box;
        background-color: #1f77b4;
        padding: 10px 0;
        margin: 0;
    }
    .marquee span {
        display: inline-block;
        padding-left: 100%;
        animation: marquee 12s linear infinite;
        font-size: 40px;
        font-weight: bold;
        color: white;
    }
    @keyframes marquee {
        0% { transform: translate(0, 0); }
        100% { transform: translate(-100%, 0); }
    }
    </style>
    <div class="marquee">
        <span>Healthcare Performance Management System</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Add professional white space at top center
    st.markdown("""
    <div style="text-align: center; padding: 30px 0; background-color: white;">
    </div>
    """, unsafe_allow_html=True)
    
    # Dashboard title
    st.title("📈 Admin Dashboard - Healthcare Performance Rankings")
    
    # Get rankings
    rankings = get_woreda_rankings()
    
    # KPI Cards
    col1, col2, col3 = st.columns(3)
    if not rankings.empty:
        with col1:
            avg_score = rankings['percentage_score'].mean()
            st.metric("Average Zone Score", f"{avg_score:.2f}%")
        
        with col2:
            top_woreda = rankings.iloc[0]
            st.metric("Top Performing Woreda", f"{top_woreda['woreda_name']} ({top_woreda['percentage_score']:.2f}%)")
        
        with col3:
            least_woreda = rankings.iloc[-1]
            st.metric("Least Performing Woreda", f"{least_woreda['woreda_name']} ({least_woreda['percentage_score']:.2f}%)")
    else:
        with col1:
            st.metric("Average Zone Score", "No Data")
        with col2:
            st.metric("Top Performing Woreda", "No Data")
        with col3:
            st.metric("Least Performing Woreda", "No Data")
    
    st.markdown("---")
    
    # Rankings Bar Chart with Enhanced Features
    st.subheader("📊 Woreda Performance Rankings")
    if not rankings.empty:
        # Add color coding based on performance
        def get_color(score):
            if score >= 80:
                return '#28a745'  # Green for high performance
            elif score >= 50:
                return '#ffc107'  # Yellow for average performance
            else:
                return '#dc3545'  # Red for low performance
        
        # Apply color coding
        rankings['bar_color'] = rankings['percentage_score'].apply(get_color)
        
        # Create enhanced bar chart
        fig = px.bar(
            rankings, 
            x='percentage_score', 
            y='woreda_name',
            orientation='h',
            title="<b style='font-size: 20px;'>Woredas Ranked by Performance Score</b>",
            labels={'percentage_score': 'Score (%)', 'woreda_name': 'Woreda'},
            color='bar_color',
            color_discrete_map='identity',
            text='percentage_score',  # Add data labels
            text_auto='.1f',  # Format to 1 decimal place
        )
        
        # Update layout for better visibility
        fig.update_layout(
            height=800,  # Increased height for better readability
            width=1200,  # Increased width
            xaxis=dict(
                title="<b>Score (%)</b>",
                range=[0, 100],  # Set X-axis range from 0 to 100%
                title_font=dict(size=14, family='Arial, sans-serif'),
                tickfont=dict(size=12, family='Arial, sans-serif')
            ),
            yaxis=dict(
                title="<b>Woreda</b>",
                title_font=dict(size=14, family='Arial, sans-serif'),
                tickfont=dict(size=11, family='Arial, sans-serif'),  # Larger font for Woreda names
                categoryorder='total ascending'  # Keep ranking order
            ),
            title_font=dict(size=20, family='Arial, sans-serif'),
            showlegend=False,  # Hide legend since colors are self-explanatory
            margin=dict(l=20, r=20, t=60, b=20)  # Adjust margins
        )
        
        # Update text labels positioning
        fig.update_traces(
            texttemplate='%{text:.1f}%',  # Show percentage with % symbol
            textposition='outside',  # Position labels outside bars
            textfont=dict(size=10, family='Arial, sans-serif', color='black'),
            insidetextfont=dict(color='white'),
            marker_line_width=1,
            marker_line_color='black'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add color legend
        st.markdown("""
        <div style="display: flex; justify-content: center; gap: 30px; margin: 20px 0;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 20px; height: 20px; background-color: #28a745; border: 1px solid black;"></div>
                <span style="font-weight: bold;">High Performance (≥80%)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 20px; height: 20px; background-color: #ffc107; border: 1px solid black;"></div>
                <span style="font-weight: bold;">Average Performance (50-79%)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 20px; height: 20px; background-color: #dc3545; border: 1px solid black;"></div>
                <span style="font-weight: bold;">Low Performance (<50%)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Data Values Summary
    st.subheader("📊 Data Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        avg_score = rankings['total_score'].mean()
        st.metric("Average Score", f"{avg_score:.1f}/105")
    with col2:
        max_score = rankings['total_score'].max()
        st.metric("Highest Score", f"{max_score:.1f}/105")
    with col3:
        total_woredas = len(rankings)
        st.metric("Total Woredas", total_woredas)
    
    # Ranking Table with Conditional Formatting
    st.subheader("📋 Detailed Ranking Table")
    
    # Create ranking table with conditional formatting
    ranking_data = []
    for rank, row in enumerate(rankings.itertuples(), 1):
        percentage = row.percentage_score
        
        # Apply conditional formatting with 3-color scheme
        if percentage >= 75:
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
            'Total Score (Out of 105)': f"{row.total_score:.1f}",
            'Final Percentage (%)': percentage_display,
            'Color Class': percentage_class
        })
    
    ranking_df = pd.DataFrame(ranking_data)
    
    # Apply custom CSS for conditional formatting
    st.markdown("""
    <style>
    .dataframe td {
        font-size: 14px !important;
        font-weight: bold !important;
    }
    .dataframe th {
        font-size: 16px !important;
        font-weight: bold !important;
        background-color: #1f77b4 !important;
        color: white !important;
    }
    .high-percentage {
        background-color: #d4edda !important;
        color: #155724 !important;
        font-weight: bold !important;
    }
    .medium-percentage {
        background-color: #fff3cd !important;
        color: #856404 !important;
        font-weight: bold !important;
    }
    .low-percentage {
        background-color: #f8d7da !important;
        color: #721c24 !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display ranking table with color coding using HTML
    ranking_html = """
    <table style="width: 100%; border-collapse: collapse; font-size: 18px; font-weight: bold; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <thead>
            <tr style="background: linear-gradient(135deg, #1f77b4, #2e7cd6); color: white; font-weight: 900;">
                <th style="padding: 15px; border: none; text-align: center; font-size: 20px;">Rank</th>
                <th style="padding: 15px; border: none; text-align: center; font-size: 20px;">Woreda Name</th>
                <th style="padding: 15px; border: none; text-align: center; font-size: 20px;">Total Score (Out of 105)</th>
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
            cell_class = 'high-percentage-cell'
        elif percentage >= 60:
            bg_color = '#fff3cd'
            text_color = '#856404'
            emoji = '🟡'
            border_color = '#ffc107'
            cell_class = 'medium-percentage-cell'
        elif percentage >= 40:
            bg_color = '#fff3cd'
            text_color = '#856404'
            emoji = '🟡'
            border_color = '#ffc107'
            cell_class = 'medium-percentage-cell'
        else:
            bg_color = '#f8d7da'
            text_color = '#721c24'
            emoji = '🔴'
            border_color = '#dc3545'
            cell_class = 'low-percentage-cell'
        
        ranking_html += f"""
            <tr style="background-color: {'white' if _ % 2 == 0 else '#f8f9fa'}; transition: all 0.3s ease;">
                <td style="padding: 12px; border: none; font-weight: bold; text-align: center; color: #2c3e50;">{row['Rank']}</td>
                <td style="padding: 12px; border: none; font-weight: bold; text-align: left; color: #2c3e50;">{row['Woreda Name']}</td>
                <td style="padding: 12px; border: none; font-weight: bold; text-align: center; background: linear-gradient(135deg, #e3f2fd, #bbdefb); color: #1565c0; font-size: 20px; border: 2px solid #1f77b4; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">{row['Total Score (Out of 105)']}</td>
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
    .high-percentage-cell {
        animation: pulse-green 2s infinite;
    }
    .medium-percentage-cell {
        animation: pulse-yellow 2s infinite;
    }
    .low-percentage-cell {
        animation: pulse-red 2s infinite;
    }
    @keyframes pulse-green {
        0%, 100% { box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.4); }
        50% { box-shadow: 0 0 0 8px rgba(40, 167, 69, 0); }
    }
    @keyframes pulse-yellow {
        0%, 100% { box-shadow: 0 0 0 0 rgba(255, 193, 7, 0.4); }
        50% { box-shadow: 0 0 0 8px rgba(255, 193, 7, 0); }
    }
    @keyframes pulse-red {
        0%, 100% { box-shadow: 0 0 0 0 rgba(220, 53, 69, 0.4); }
        50% { box-shadow: 0 0 0 8px rgba(220, 53, 69, 0); }
    }
    table tr:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    </style>
    """
    
    html(ranking_html, height=600)
    
    # Detailed Analysis
    st.subheader("🔍 Detailed Woreda Analysis")
    selected_woreda = st.selectbox("Select Woreda for Detailed Analysis", get_woredas())
    
    if selected_woreda:
        detailed_data = get_woreda_detailed_data(selected_woreda)
        if not detailed_data.empty:
            # Line Chart (replacing Radar Chart)
            categories = [
                'Medical Service', 'RMH', 'Pharmacy & Logistic', 'Ultrasound', 'APTS',
                'Community Pharmacy', 'DM Test', 'EPI', 'Child Health', 'TB & Leprosy',
                'PHEM', 'CBHI', 'Finance', 'Plan', 'WT', 'Full EMR', 'EPI Modernization',
                'Zero Dose', 'Multi-Sectoral', 'Cash Program', 'Hygiene & Sanitation',
                'HIV/STI'
            ]
            values = [
                detailed_data['medical_service'].sum(),
                detailed_data['rmh'].sum(),
                detailed_data['pharmacy_logistic'].sum(),
                detailed_data['ultrasound'].sum(),
                detailed_data['apts'].sum(),
                detailed_data['community_pharmacy'].sum(),
                detailed_data['dm_test'].sum(),
                detailed_data['epi'].sum(),
                detailed_data['child_health'].sum(),
                detailed_data['tb_leprosy'].sum(),
                detailed_data['phem'].sum(),
                detailed_data['cbhi'].sum(),
                detailed_data['finance'].sum(),
                detailed_data['plan'].sum(),
                detailed_data['wt'].sum(),
                detailed_data['full_emr'].sum(),
                detailed_data['epi_modernization'].sum(),
                detailed_data['zero_dose'].sum(),
                detailed_data['multi_sectoral'].sum(),
                detailed_data['cash_program'].sum(),
                detailed_data['hygiene_sanitation'].sum(),
                detailed_data['hiv_sti'].sum() if 'hiv_sti' in detailed_data.columns else 0
            ]
            
            # Create line chart
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=categories,
                y=values,
                mode='lines+markers+text',  # Add markers and text
                name=selected_woreda,
                line=dict(color='#1f77b4', width=6),  # Much thicker line for better visibility
                marker=dict(size=10, color='#1f77b4', symbol='circle'),  # Add visible markers
                text=values,
                textposition='top center',
                textfont=dict(size=12, color='black', family='Arial, sans-serif')  # Larger, bold text
            ))
            
            fig_line.update_layout(
                title=f"<b style='font-size: 18px;'>{selected_woreda} Performance Line Chart</b>",
                xaxis_title="<b>Departments</b>",
                yaxis_title="<b>Score</b>",
                xaxis=dict(
                    tickangle=90,  # Rotate to 90 degrees for better readability
                    tickfont=dict(size=14, family='Arial, sans-serif'),  # Larger font
                    title_font=dict(size=16, family='Arial, sans-serif'),  # Larger title
                    automargin=True  # Auto-adjust margins
                ),
                yaxis=dict(
                    range=[0, max(values) + 1 if values else 10],
                    title_font=dict(size=16, family='Arial, sans-serif'),  # Larger title
                    tickfont=dict(size=14, family='Arial, sans-serif')  # Larger font
                ),
                height=700,  # Increased height for better visibility
                showlegend=True,
                margin=dict(l=80, r=80, t=100, b=150)  # Increased margins for labels
            )
            
            st.plotly_chart(fig_line, use_container_width=True)
            
            # Data Table - Display all Woredas with 0 data and remove entered_by header
            st.subheader("📋 Detailed Data")
            
            # Add CSS for bold table text and larger font
            st.markdown("""
            <style>
            .dataframe {
                font-size: 18px !important;
                font-weight: bold !important;
            }
            .dataframe th {
                font-size: 20px !important;
                font-weight: bold !important;
                background-color: #1f77b4 !important;
                color: white !important;
                padding: 15px !important;
                text-align: center !important;
            }
            .dataframe td {
                font-size: 18px !important;
                font-weight: bold !important;
                padding: 12px !important;
                border: 1px solid #ddd !important;
                text-align: center !important;
                height: 50px !important;  /* Increased row height */
            }
            /* Emphasize Total Score and Final Percentage columns */
            .dataframe td:nth-last-child(1),
            .dataframe td:nth-last-child(2) {
                background-color: #e3f2fd !important;
                color: #1565c0 !important;
                font-size: 20px !important;
                font-weight: 900 !important;
                border: 2px solid #1f77b4 !important;
            }
            /* Color coding for Final Percentage column */
            .high-percentage-cell {
                background-color: #d4edda !important;
                color: #155724 !important;
                font-weight: 900 !important;
            }
            .medium-percentage-cell {
                background-color: #fff3cd !important;
                color: #856404 !important;
                font-weight: 900 !important;
            }
            .low-percentage-cell {
                background-color: #f8d7da !important;
                color: #721c24 !important;
                font-weight: 900 !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Get all Woredas data
            all_data = get_performance_data()
            
            # Remove unwanted columns and group by woreda_name
            if not all_data.empty:
                # Remove entered_by and department columns
                columns_to_drop = ['entered_by', 'department']
                existing_columns_to_drop = [col for col in columns_to_drop if col in all_data.columns]
                
                if existing_columns_to_drop:
                    all_data = all_data.drop(columns=existing_columns_to_drop)
                
                # Group by woreda_name and sum all performance indicators
                numeric_columns = all_data.select_dtypes(include=['number']).columns
                grouped_data = all_data.groupby('woreda_name')[numeric_columns].sum().reset_index()
                
                # Calculate total score and percentage
                performance_indicators = [
                    'medical_service', 'rmh', 'pharmacy_logistic', 'ultrasound', 'apts',
                    'community_pharmacy', 'dm_test', 'epi', 'child_health', 'tb_leprosy',
                    'phem', 'cbhi', 'finance', 'plan', 'wt', 'full_emr', 'epi_modernization',
                    'zero_dose', 'multi_sectoral', 'cash_program', 'hygiene_sanitation',
                    'hiv_sti'
                ]
                
                # Calculate total score (sum of all indicators)
                grouped_data['total_score'] = grouped_data[performance_indicators].sum(axis=1)
                
                # Calculate percentage (total_score / 105 * 100)
                grouped_data['percentage'] = (grouped_data['total_score'] / 105 * 100).round(2)
                
                # Reorder columns to show id, woreda_name, indicators, total_score, percentage
                if 'id' in grouped_data.columns:
                    final_columns = ['id', 'woreda_name'] + performance_indicators + ['total_score', 'percentage']
                else:
                    final_columns = ['woreda_name'] + performance_indicators + ['total_score', 'percentage']
                
                # Filter to only include columns that exist
                final_columns = [col for col in final_columns if col in grouped_data.columns]
                
                final_data = grouped_data[final_columns]
                
                # Rename columns for better display
                column_rename_map = {
                    'total_score': 'Total Score (Out of 105)',
                    'percentage': 'Percentage (%)'
                }
                final_data = final_data.rename(columns=column_rename_map)
                
                st.dataframe(final_data, use_container_width=True)
            else:
                st.info("No performance data available in the system.")
        else:
            st.info(f"No performance data available for {selected_woreda}")
    else:
        st.info("No performance data available. Please have department heads enter data first.")
    
    # Add footer with enhanced visibility
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 30px 0; background-color: #f8f9fa; border-top: 3px solid #1f77b4; margin-top: 40px;">
        <p style="color: #1f77b4; font-size: 18px; font-weight: bold; margin: 10px 0;">© 2026 All Rights Reserved</p>
        <p style="color: #333; font-size: 16px; margin: 8px 0;">Developed by <strong style="color: #1f77b4;">Abe_Technology</strong></p>
        <p style="color: #333; font-size: 16px; margin: 8px 0;">Contact via Telegram: <strong style="color: #1f77b4;">AI_Technology</strong></p>
    </div>
    """, unsafe_allow_html=True)

def super_admin_dashboard():
    st.title("🔧 Super Admin Dashboard - Full Control")
    
    # Tabs for different functions
    tab1, tab2, tab3 = st.tabs(["📊 Rankings", "✏️ Edit Data", "👥 User Management"])
    
    with tab1:
        admin_dashboard()
    
    with tab2:
        st.subheader("✏️ Edit Performance Data")
        
        # Get all data
        df = get_performance_data()
        
        if not df.empty:
            # Select record to edit
            record_id = st.selectbox(
                "Select Record to Edit",
                options=df['id'].tolist(),
                format_func=lambda x: f"ID: {x} - {df[df['id']==x]['woreda_name'].iloc[0]} - {df[df['id']==x]['department'].iloc[0]}"
            )
            
            if record_id:
                record = df[df['id'] == record_id].iloc[0]
                
                st.write(f"**Editing:** {record['woreda_name']} - {record['department']}")
                
                # Edit form
                col1, col2 = st.columns(2)
                
                with col1:
                    new_medical = st.number_input("Medical Service", value=float(record['medical_service']))
                    new_rmh = st.number_input("RMH", value=float(record['rmh']))
                    new_pharmacy = st.number_input("Pharmacy & Logistic", value=float(record['pharmacy_logistic']))
                    new_ultrasound = st.number_input("Ultrasound", value=float(record['ultrasound']))
                    new_apts = st.number_input("APTS", value=float(record['apts']))
                    new_community_pharmacy = st.number_input("Community Pharmacy", value=float(record['community_pharmacy']))
                    new_dm_test = st.number_input("DM Test", value=float(record['dm_test']))
                    new_epi = st.number_input("EPI", value=float(record['epi']))
                    new_child_health = st.number_input("Child Health", value=float(record['child_health']))
                    new_tb_leprosy = st.number_input("TB & Leprosy", value=float(record['tb_leprosy']))
                    new_phem = st.number_input("PHEM", value=float(record['phem']))
                
                with col2:
                    new_cbhi = st.number_input("CBHI", value=float(record['cbhi']))
                    new_finance = st.number_input("Finance", value=float(record['finance']))
                    new_plan = st.number_input("Plan", value=float(record['plan']))
                    new_wt = st.number_input("WT", value=float(record['wt']))
                    new_full_emr = st.number_input("Full EMR", value=float(record['full_emr']))
                    new_epi_modernization = st.number_input("EPI Modernization", value=float(record['epi_modernization']))
                    new_zero_dose = st.number_input("Zero Dose", value=float(record['zero_dose']))
                    new_multi_sectoral = st.number_input("Multi-Sectoral", value=float(record['multi_sectoral']))
                    new_cash_program = st.number_input("Cash Program", value=float(record['cash_program']))
                    new_hygiene = st.number_input("Hygiene & Sanitation", value=float(record['hygiene_sanitation']))
                
                col1, col2, col3 = st.columns(3)
                with col2:
                    if st.button("Update Record", use_container_width=True):
                        updated_data = {
                            'medical_service': new_medical, 'rmh': new_rmh, 'pharmacy_logistic': new_pharmacy,
                            'ultrasound': new_ultrasound, 'apts': new_apts, 'community_pharmacy': new_community_pharmacy,
                            'dm_test': new_dm_test, 'epi': new_epi, 'child_health': new_child_health,
                            'tb_leprosy': new_tb_leprosy, 'phem': new_phem, 'cbhi': new_cbhi,
                            'finance': new_finance, 'plan': new_plan, 'wt': new_wt,
                            'full_emr': new_full_emr, 'epi_modernization': new_epi_modernization,
                            'zero_dose': new_zero_dose, 'multi_sectoral': new_multi_sectoral,
                            'cash_program': new_cash_program, 'hygiene_sanitation': new_hygiene
                        }
                        save_performance_data(record['woreda_name'], record['department'], updated_data, st.session_state.username)
                        st.success("Record updated successfully!")
                        st.rerun()
                    
                    if st.button("Delete Record", use_container_width=True):
                        conn = sqlite3.connect('healthcare_performance.db')
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM performance_data WHERE id = ?", (record_id,))
                        conn.commit()
                        conn.close()
                        st.success("Record deleted successfully!")
                        st.rerun()
        
        # Show all data
        st.subheader("📋 All Performance Data")
        st.dataframe(df, use_container_width=True)
    
    with tab3:
        st.subheader("👥 User Management")
        st.info("User management features can be added here")

# Main application
def main():
    # Initialize database
    init_db()
    
    # Add full screen CSS
    st.markdown("""
    <style>
    /* Full screen width */
    .main .block-container {
        max-width: 100% !important;
        padding: 2rem 1rem !important;
    }
    
    /* Remove sidebar padding */
    .css-1d391kg {
        padding: 0rem !important;
    }
    
    /* Full width for content */
    .stApp {
        max-width: 100% !important;
    }
    
    /* Make tables full width */
    .dataframe {
        width: 100% !important;
    }
    
    /* Make charts full width */
    .js-plotly-plot {
        width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'role' not in st.session_state:
        st.session_state.role = ""
    if 'department' not in st.session_state:
        st.session_state.department = ""
    if 'current_view' not in st.session_state:
        st.session_state.current_view = "Data Entry"
    
    # Check authentication
    if not st.session_state.authenticated:
        login_page()
    else:
        # Sidebar with navigation and logout
        with st.sidebar:
            st.title("🏥 Navigation")
            st.write(f"**Logged in as:** {st.session_state.username}")
            st.write(f"**Role:** {st.session_state.role}")
            if st.session_state.department:
                st.write(f"**Department:** {st.session_state.department}")
            
            st.markdown("---")
            
            # Show current form
            st.info(f"📝 **Current Form:** {st.session_state.current_view}")
            
            # Navigation options based on role
            if st.session_state.role == 'Department Head':
                # Department heads only see data entry
                st.session_state.current_view = "Data Entry"
                st.info("Only Data Entry available for Department Heads")
                
            elif st.session_state.role == 'Admin':
                # Admin can switch between data entry and dashboard
                view_options = ["Data Entry", "Report"]
                selected_view = st.selectbox("Select View", view_options, index=0 if st.session_state.current_view == "Data Entry" else 1)
                st.session_state.current_view = selected_view
                
            elif st.session_state.role == 'Super Admin':
                # Super Admin has all options
                view_options = ["Data Entry", "Report", "Edit Data", "User Management"]
                selected_view = st.selectbox("Select View", view_options, index=["Data Entry", "Report", "Edit Data", "User Management"].index(st.session_state.current_view) if st.session_state.current_view in ["Data Entry", "Report", "Edit Data", "User Management"] else 0)
                st.session_state.current_view = selected_view
            
            st.markdown("---")
            
            # Logout button
            if st.button("🚪 Logout", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.success("Logged out successfully!")
                st.rerun()
        
        # Main content based on role and current view
        if st.session_state.role == 'Department Head':
            department_head_interface(st.session_state.department, st.session_state.username)
            
        elif st.session_state.role == 'Admin':
            if st.session_state.current_view == "Data Entry":
                st.info("As Admin, you can enter data for any department. Please select a department:")
                # Allow admin to enter data for any department
                departments = [
                    "Cash", "EPI", "DM Test", "Ultrasound",
                    "Community Pharmacy", "Zero Dose", "Full EMR", "APTS", "RMH",
                    "Child Health", "EPI", "TB & Leprosy", "Hayine & Sanitation", "HIV & STI",
                    "Pharmacy & Logistic", "Medical Service", "PHEM", "Multi-Sectoral",
                    "CBHI", "Finance", "Plan", "WT"
                ]
                selected_dept = st.selectbox("Select Department for Data Entry", departments)
                if selected_dept:
                    department_head_interface(selected_dept, st.session_state.username)
            elif st.session_state.current_view == "Report":
                admin_dashboard()
                
        elif st.session_state.role == 'Super Admin':
            if st.session_state.current_view == "Data Entry":
                st.info("As Super Admin, you can enter data for any department:")
                departments = [
                    "Cash", "EPI", "DM Test", "Ultrasound",
                    "Community Pharmacy", "Zero Dose", "Full EMR", "APTS", "RMH",
                    "Child Health", "EPI", "TB & Leprosy", "Hayine & Sanitation", "HIV & STI",
                    "Pharmacy & Logistic", "Medical Service", "PHEM", "Multi-Sectoral",
                    "CBHI", "Finance", "Plan", "WT"
                ]
                selected_dept = st.selectbox("Select Department for Data Entry", departments)
                if selected_dept:
                    department_head_interface(selected_dept, st.session_state.username)
            elif st.session_state.current_view == "Report":
                admin_dashboard()
                
if __name__ == "__main__":
    main()

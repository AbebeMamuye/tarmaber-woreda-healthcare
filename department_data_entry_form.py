import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime
import os

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

# Get woredas
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

# Department Head Interface - Enhanced Data Entry Form
def department_head_interface(department, username):
    st.title(f"📊 {department} Data Entry")
    st.markdown(f"**Department:** {department}")
    st.markdown(f"**Logged in as:** {username}")
    
    # Column info for department with exact same structure
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
            
            # Add department-specific instructions
            if department == 'Medical Service':
                st.info("🏥 Medical Service: Enter scores for all 4 Health Centers (Max: 15 points each)")
            elif department == 'CBHI':
                st.info("💰 CBHI: Enter scores for all 4 Health Centers (Max: 10 points each)")
            elif department in ['EPI', 'TB & Leprosy', 'Child Health', 'PHEM']:
                st.info(f"🏥 {department}: Enter scores for all 4 Health Centers (Max: {info['max']} points each)")
            elif department in ['Finance', 'Plan', 'WT']:
                st.info(f"📊 {department}: Enter scores for all 4 Health Centers (Max: {info['max']} points each)")
            elif department == 'RMH':
                st.info("🏥 RMH: Enter scores for all 4 Health Centers (Max: 10 points each)")
            elif department in ['Ultrasound', 'APTS', 'Community Pharmacy', 'DM Test']:
                st.info(f"🔬 {department}: Enter scores for all 4 Health Centers (Max: {info['max']} points each)")
            elif department in ['EPI Modernization', 'Zero Dose', 'Multi-Sectoral', 'Cash Program']:
                st.info(f"🆕 {department}: Enter scores for all 4 Health Centers (Max: {info['max']} points each)")
            elif department in ['Full EMR']:
                st.info("💻 Full EMR: Enter scores for all 4 Health Centers (Max: 5 points each)")
            elif department in ['Hygiene & Sanitation', 'HIV/STI']:
                st.info(f"🧼 {department}: Enter scores for all 4 Health Centers (Max: {info['max']} points each)")
            
            woredas = get_woredas()
            input_data = {}
            
            # Create columns for better layout
            cols = st.columns(3)
            
            for i, woreda in enumerate(woredas):
                col = cols[i % 3]
                with col:
                    input_data[woreda] = st.number_input(
                        f"{woreda}",
                        min_value=0.0,
                        max_value=float(info['max']),
                        value=0.0,
                        step=0.1,
                        key=f"{key}_{woreda}",
                        help=f"Max: {info['max']} points"
                    )
            
            st.markdown("---")
            
            # Save button with confirmation
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(f"💾 Save {info['label']} Data", use_container_width=True, type="primary"):
                    success_count = 0
                    error_count = 0
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, (woreda, value) in enumerate(input_data.items()):
                        data = {key: value}
                        if save_performance_data(woreda, department, data, username):
                            success_count += 1
                        else:
                            error_count += 1
                        
                        # Update progress
                        progress = (i + 1) / len(input_data)
                        progress_bar.progress(progress)
                        status_text.text(f"Saving data... {i + 1}/{len(input_data)} Health Centers")
                    
                    progress_bar.empty()
                    status_text.empty()
                    
                    if success_count > 0:
                        st.success(f"✅ Successfully saved {info['label']} data for {success_count} Health Centers!")
                        if error_count > 0:
                            st.warning(f"⚠️ Failed to save data for {error_count} Health Centers")
                    else:
                        st.error(f"❌ Failed to save {info['label']} data")
            
            st.markdown("---")
    
    # Show current data summary
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
        
        if not df.empty:
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
        else:
            st.info(f"No data available for {department} yet.")
        
        conn.close()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")

# Main function for testing
def main():
    # Simulate login for testing
    st.session_state.authenticated = True
    st.session_state.role = "Department Head"
    st.session_state.department = "EPI"  # Change this to test different departments
    st.session_state.username = "epi"
    
    # Show the department interface
    if st.session_state.authenticated and st.session_state.role == "Department Head":
        department_head_interface(st.session_state.department, st.session_state.username)
    else:
        st.error("Please login as a Department Head to access this interface.")

if __name__ == "__main__":
    main()

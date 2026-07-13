import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import hashlib

# Page configuration
st.set_page_config(
    page_title="Healthcare Performance System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide Streamlit branding
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Department structure with indicators and weights
DEPARTMENTS = {
    "EPI": {
        "indicators": ["EPI Coverage", "Cold Chain Management", "Vaccine Stock", "Reporting Quality"],
        "max_score": 5.0
    },
    "Child Health": {
        "indicators": ["Growth Monitoring", "Nutrition Programs", "Child Mortality Rate", "Immunization Follow-up"],
        "max_score": 5.0
    },
    "TB & Leprosy": {
        "indicators": ["TB Case Detection", "Treatment Success Rate", "Leprosy Screening", "Contact Tracing"],
        "max_score": 5.0
    },
    "PHEM": {
        "indicators": ["Disease Surveillance", "Outbreak Response", "Reporting Timeliness", "Data Quality"],
        "max_score": 5.0
    },
    "CBHI": {
        "indicators": ["Enrollment Rate", "Premium Collection", "Claims Processing", "Member Satisfaction"],
        "max_score": 10.0
    },
    "Finance": {
        "indicators": ["Budget Execution", "Financial Reporting", "Revenue Collection", "Audit Compliance"],
        "max_score": 5.0
    },
}

DEPARTMENTS.update({
    "Plan": {
        "indicators": ["Planning Quality", "Implementation Rate", "Monitoring & Evaluation", "Reporting"],
        "max_score": 5.0
    },
    "WT": {
        "indicators": ["Workforce Planning", "Training Programs", "Staff Retention", "Performance Management"],
        "max_score": 5.0
    },
    "Medical Service": {
        "indicators": ["Patient Load", "Service Quality", "Equipment Availability", "Patient Satisfaction"],
        "max_score": 15.0
    },
    "RMH": {
        "indicators": ["Maternal Health", "Delivery Services", "ANC Coverage", "PNC Follow-up"],
        "max_score": 10.0
    },
    "Pharmacy & Logistic": {
        "indicators": ["Drug Availability", "Stock Management", "Expiry Control", "Distribution Efficiency"],
        "max_score": 5.0
    }
})

WOREDAS = [
    "Woreda 1", "Woreda 2", "Woreda 3", "Woreda 4", "Woreda 5",
    "Woreda 6", "Woreda 7", "Woreda 8", "Woreda 9", "Woreda 10",
    "Woreda 11", "Woreda 12", "Woreda 13", "Woreda 14", "Woreda 15",
    "Woreda 16", "Woreda 17", "Woreda 18", "Woreda 19", "Woreda 20",
    "Woreda 21", "Woreda 22", "Woreda 23"
]

USERS = {
    "epi": {"password": "EPI@2024", "role": "department_head", "department": "EPI"},
    "child_health": {"password": "ChildHealth@2024", "role": "department_head", "department": "Child Health"},
    "tb": {"password": "TB@2024", "role": "department_head", "department": "TB & Leprosy"},
    "phem": {"password": "PHEM@2024", "role": "department_head", "department": "PHEM"},
    "cbhi": {"password": "CBHI@2024", "role": "department_head", "department": "CBHI"},
    "finance": {"password": "Finance@2024", "role": "department_head", "department": "Finance"},
    "plan": {"password": "Plan@2024", "role": "department_head", "department": "Plan"},
    "wt": {"password": "WT@2024", "role": "department_head", "department": "WT"},
    "medical": {"password": "Medical@2024", "role": "department_head", "department": "Medical Service"},
    "rmh": {"password": "RMH@2024", "role": "department_head", "department": "RMH"},
    "pharmacy": {"password": "Pharmacy@2024", "role": "department_head", "department": "Pharmacy & Logistic"},
    "admin": {"password": "admin@2018", "role": "admin", "department": None},
    "superadmin": {"password": "super@2024", "role": "superadmin", "department": None}
}

DATA_FILE = "performance_data.csv"

def verify_user(username, password):
    if username in USERS:
        if USERS[username]["password"] == password:
            return USERS[username]
    return None

def load_data():
    """Load data from CSV file"""
    if Path(DATA_FILE).exists():
        return pd.read_csv(DATA_FILE)
    else:
        columns = ["Woreda", "Department", "Indicator", "Score", "Entered_By"]
        return pd.DataFrame(columns=columns)

def save_data(df):
    """Save data to CSV file"""
    df.to_csv(DATA_FILE, index=False)

def calculate_woreda_scores(df):
    """Calculate total scores and percentages for each woreda"""
    results = []
    
    for woreda in WOREDAS:
        woreda_data = df[df["Woreda"] == woreda]
        total_score = 0
        
        for dept, config in DEPARTMENTS.items():
            dept_data = woreda_data[woreda_data["Department"] == dept]
            if not dept_data.empty:
                dept_score = dept_data["Score"].sum()
                total_score += dept_score
        
        max_possible = sum(config["max_score"] for config in DEPARTMENTS.values())
        percentage = (total_score / max_possible * 100) if max_possible > 0 else 0
        
        results.append({
            "Woreda": woreda,
            "Total Score": round(total_score, 2),
            "Percentage": round(percentage, 2)
        })
    
    return pd.DataFrame(results).sort_values("Total Score", ascending=False).reset_index(drop=True)

def login_page():
    """Display login page"""
    st.title("🏥 Healthcare Performance Management System")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", use_container_width=True):
            user_info = verify_user(username, password)
            if user_info:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = user_info["role"]
                st.session_state.department = user_info["department"]
                st.rerun()
            else:
                st.error("Invalid username or password")

def department_head_interface():
    """Interface for department heads to enter data"""
    dept = st.session_state.department
    username = st.session_state.username
    
    st.title(f"📊 {dept} - Data Entry")
    st.markdown(f"**Logged in as:** {username} | **Role:** Department Head")
    st.markdown("---")
    
    df = load_data()
    woreda = st.selectbox("Select Woreda", WOREDAS, key="dept_woreda")
    
    st.subheader(f"Enter Performance Data for {woreda}")
    
    indicators = DEPARTMENTS[dept]["indicators"]
    max_score = DEPARTMENTS[dept]["max_score"]
    score_per_indicator = max_score / len(indicators)
    
    existing_data = df[(df["Woreda"] == woreda) & (df["Department"] == dept)]
    
    scores = {}
    cols = st.columns(2)
    
    for idx, indicator in enumerate(indicators):
        with cols[idx % 2]:
            existing_score = 0
            if not existing_data.empty:
                indicator_data = existing_data[existing_data["Indicator"] == indicator]
                if not indicator_data.empty:
                    existing_score = float(indicator_data.iloc[0]["Score"])
            
            scores[indicator] = st.number_input(
                f"{indicator}",
                min_value=0.0,
                max_value=score_per_indicator,
                value=existing_score,
                step=0.1,
                key=f"score_{indicator}"
            )
    
    total_score = sum(scores.values())
    percentage = (total_score / max_score * 100) if max_score > 0 else 0
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Score", f"{total_score:.2f}")
    with col2:
        st.metric("Max Possible", f"{max_score:.2f}")
    with col3:
        st.metric("Percentage", f"{percentage:.2f}%")
    
    if st.button("💾 Save Data", use_container_width=True, type="primary"):
        df = df[~((df["Woreda"] == woreda) & (df["Department"] == dept))]
        
        new_rows = []
        for indicator, score in scores.items():
            new_rows.append({
                "Woreda": woreda,
                "Department": dept,
                "Indicator": indicator,
                "Score": score,
                "Entered_By": username
            })
        
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        save_data(df)
        st.success(f"✅ Data saved successfully for {woreda} - {dept}")
        st.rerun()

def admin_dashboard():
    """View-only dashboard for admin"""
    st.title("📈 Admin Dashboard")
    st.markdown(f"**Logged in as:** {st.session_state.username} | **Role:** Admin (View Only)")
    st.markdown("---")
    
    df = load_data()
    
    if df.empty:
        st.info("No data available yet. Department heads need to enter data.")
        return
    
    rankings = calculate_woreda_scores(df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_score = rankings["Total Score"].mean()
        st.metric("Average Score", f"{avg_score:.2f}")
    
    with col2:
        top_woreda = rankings.iloc[0]
        st.metric("Top Performer", top_woreda["Woreda"], f"{top_woreda['Total Score']:.2f}")
    
    with col3:
        bottom_woreda = rankings.iloc[-1]
        st.metric("Needs Improvement", bottom_woreda["Woreda"], f"{bottom_woreda['Total Score']:.2f}")
    
    with col4:
        avg_percentage = rankings["Percentage"].mean()
        st.metric("Average Percentage", f"{avg_percentage:.2f}%")
    
    st.markdown("---")
    st.subheader("📊 Woreda Rankings")
    
    rankings_with_rank = rankings.copy()
    rankings_with_rank.insert(0, "Rank", range(1, len(rankings_with_rank) + 1))
    
    html_table = """
    <style>
    .ranking-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-size: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .ranking-table thead tr {
        background-color: #1f77b4;
        color: white;
        text-align: left;
        font-weight: bold;
    }
    .ranking-table th, .ranking-table td {
        padding: 12px 15px;
        border: 1px solid #ddd;
    }
    .ranking-table tbody tr {
        border-bottom: 1px solid #ddd;
    }
    .ranking-table tbody tr:nth-of-type(even) {
        background-color: #f3f3f3;
    }
    .ranking-table tbody tr:hover {
        background-color: #e8f4f8;
    }
    .rank-1 { background-color: #ffd700 !important; font-weight: bold; }
    .rank-2 { background-color: #c0c0c0 !important; font-weight: bold; }
    .rank-3 { background-color: #cd7f32 !important; font-weight: bold; }
    </style>
    <table class="ranking-table">
        <thead>
            <tr>
                <th>Rank</th>
                <th>Woreda</th>
                <th>Total Score</th>
                <th>Percentage</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for idx, row in rankings_with_rank.iterrows():
        rank_class = f"rank-{row['Rank']}" if row['Rank'] <= 3 else ""
        html_table += f"""
            <tr class="{rank_class}">
                <td>{row['Rank']}</td>
                <td>{row['Woreda']}</td>
                <td>{row['Total Score']}</td>
                <td>{row['Percentage']}%</td>
            </tr>
        """
    
    html_table += """
        </tbody>
    </table>
    """
    
    st.markdown(html_table, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("📊 Performance Visualization")
    
    fig = px.bar(
        rankings,
        x="Woreda",
        y="Total Score",
        title="Woreda Performance Comparison",
        color="Total Score",
        color_continuous_scale="Blues"
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("📋 Detailed Department Data")
    
    selected_woreda = st.selectbox("Select Woreda for Details", WOREDAS, key="admin_woreda_detail")
    woreda_data = df[df["Woreda"] == selected_woreda]
    
    if not woreda_data.empty:
        dept_summary = []
        for dept in DEPARTMENTS.keys():
            dept_data = woreda_data[woreda_data["Department"] == dept]
            if not dept_data.empty:
                dept_score = dept_data["Score"].sum()
                max_score = DEPARTMENTS[dept]["max_score"]
                dept_summary.append({
                    "Department": dept,
                    "Score": round(dept_score, 2),
                    "Max Score": max_score,
                    "Percentage": round((dept_score / max_score * 100), 2)
                })
        
        if dept_summary:
            st.dataframe(pd.DataFrame(dept_summary), use_container_width=True)
        else:
            st.info(f"No data available for {selected_woreda}")
    else:
        st.info(f"No data available for {selected_woreda}")

def super_admin_dashboard():
    """Full access dashboard for super admin"""
    st.title("🔧 Super Admin Dashboard")
    st.markdown(f"**Logged in as:** {st.session_state.username} | **Role:** Super Admin (Full Access)")
    st.markdown("---")
    
    df = load_data()
    
    tab1, tab2, tab3 = st.tabs(["📊 View Rankings", "✏️ Edit Data", "📥 Data Management"])
    
    with tab1:
        if df.empty:
            st.info("No data available yet.")
        else:
            rankings = calculate_woreda_scores(df)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_score = rankings["Total Score"].mean()
                st.metric("Average Score", f"{avg_score:.2f}")
            
            with col2:
                top_woreda = rankings.iloc[0]
                st.metric("Top Performer", top_woreda["Woreda"], f"{top_woreda['Total Score']:.2f}")
            
            with col3:
                bottom_woreda = rankings.iloc[-1]
                st.metric("Needs Improvement", bottom_woreda["Woreda"], f"{bottom_woreda['Total Score']:.2f}")
            
            with col4:
                avg_percentage = rankings["Percentage"].mean()
                st.metric("Average Percentage", f"{avg_percentage:.2f}%")
            
            st.markdown("---")
            st.subheader("📊 Woreda Rankings")
            
            rankings_with_rank = rankings.copy()
            rankings_with_rank.insert(0, "Rank", range(1, len(rankings_with_rank) + 1))
            
            html_table = """
            <style>
            .ranking-table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                font-size: 16px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            .ranking-table thead tr {
                background-color: #1f77b4;
                color: white;
                text-align: left;
                font-weight: bold;
            }
            .ranking-table th, .ranking-table td {
                padding: 12px 15px;
                border: 1px solid #ddd;
            }
            .ranking-table tbody tr {
                border-bottom: 1px solid #ddd;
            }
            .ranking-table tbody tr:nth-of-type(even) {
                background-color: #f3f3f3;
            }
            .ranking-table tbody tr:hover {
                background-color: #e8f4f8;
            }
            .rank-1 { background-color: #ffd700 !important; font-weight: bold; }
          
            
            html_table = """<style>.ranking-table {width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);} .ranking-table thead tr {background-color: #1f77b4; color: white; text-align: left; font-weight: bold;} .ranking-table th, .ranking-table td {padding: 12px 15px; border: 1px solid #ddd;} .ranking-table tbody tr {border-bottom: 1px solid #ddd;} .ranking-table tbody tr:nth-of-type(even) {background-color: #f3f3f3;} .ranking-table tbody tr:hover {background-color: #e8f4f8;} .rank-1 { background-color: #ffd700 !important; font-weight: bold; } .rank-2 { background-color: #c0c0c0 !important; font-weight: bold; } .rank-3 { background-color: #cd7f32 !important; font-weight: bold; }</style><table class="ranking-table"><thead><tr><th>Rank</th><th>Woreda</th><th>Total Score</th><th>Percentage</th></tr></thead><tbody>"""
            
            for idx, row in rankings_with_rank.iterrows():
                rank_class = f"rank-{row['Rank']}" if row['Rank'] <= 3 else ""
                html_table += f'<tr class="{rank_class}"><td>{row["Rank"]}</td><td>{row["Woreda"]}</td><td>{row["Total Score"]}</td><td>{row["Percentage"]}%</td></tr>'
            
            html_table += "</tbody></table>"
            st.markdown(html_table, unsafe_allow_html=True)
            
            fig = px.bar(rankings, x="Woreda", y="Total Score", title="Woreda Performance Comparison", color="Total Score", color_continuous_scale="Blues")
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("✏️ Edit Department Data")
        
        edit_woreda = st.selectbox("Select Woreda", WOREDAS, key="edit_woreda")
        edit_dept = st.selectbox("Select Department", list(DEPARTMENTS.keys()), key="edit_dept")
        
        indicators = DEPARTMENTS[edit_dept]["indicators"]
        max_score = DEPARTMENTS[edit_dept]["max_score"]
        score_per_indicator = max_score / len(indicators)
        
        existing_data = df[(df["Woreda"] == edit_woreda) & (df["Department"] == edit_dept)]
        
        scores = {}
        cols = st.columns(2)
        
        for idx, indicator in enumerate(indicators):
            with cols[idx % 2]:
                existing_score = 0
                if not existing_data.empty:
                    indicator_data = existing_data[existing_data["Indicator"] == indicator]
                    if not indicator_data.empty:
                        existing_score = float(indicator_data.iloc[0]["Score"])
                
                scores[indicator] = st.number_input(
                    f"{indicator}",
                    min_value=0.0,
                    max_value=score_per_indicator,
                    value=existing_score,
                    step=0.1,
                    key=f"edit_score_{indicator}"
                )
        
        total_score = sum(scores.values())
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Score", f"{total_score:.2f}")
        with col2:
            st.metric("Max Possible", f"{max_score:.2f}")
        with col3:
            st.metric("Percentage", f"{percentage:.2f}%")
        
        if st.button("💾 Update Data", use_container_width=True, type="primary"):
            df = df[~((df["Woreda"] == edit_woreda) & (df["Department"] == edit_dept))]
            
            new_rows = []
            for indicator, score in scores.items():
                new_rows.append({
                    "Woreda": edit_woreda,
                    "Department": edit_dept,
                    "Indicator": indicator,
                    "Score": score,
                    "Entered_By": st.session_state.username
                })
            
            df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
            save_data(df)
            st.success(f"✅ Data updated successfully for {edit_woreda} - {edit_dept}")
            st.rerun()
    
    with tab3:
        st.subheader("📥 Data Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Export Data**")
            if not df.empty:
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name="performance_data.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.info("No data to export")
        
        with col2:
            st.write("**Delete Data**")
            delete_woreda = st.selectbox("Select Woreda to Delete", WOREDAS, key="delete_woreda")
            delete_dept = st.selectbox("Select Department to Delete", list(DEPARTMENTS.keys()), key="delete_dept")
            
            if st.button("🗑️ Delete Data", use_container_width=True, type="secondary"):
                df = df[~((df["Woreda"] == delete_woreda) & (df["Department"] == delete_dept))]
                save_data(df)
                st.success(f"✅ Data deleted for {delete_woreda} - {delete_dept}")
                st.rerun()
        
        st.markdown("---")
        st.subheader("📊 All Data")
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No data available")

def main():
    """Main application logic"""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        login_page()
    else:
        with st.sidebar:
            st.title("Navigation")
            st.markdown(f"**User:** {st.session_state.username}")
            st.markdown(f"**Role:** {st.session_state.role.replace('_', ' ').title()}")
            
            if st.session_state.department:
                st.markdown(f"**Department:** {st.session_state.department}")
            
            st.markdown("---")
            
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.session_state.role = None
                st.session_state.department = None
                st.rerun()
        
        if st.session_state.role == "department_head":
            department_head_interface()
        elif st.session_state.role == "admin":
            admin_dashboard()
        elif st.session_state.role == "superadmin":
            super_admin_dashboard()

if __name__ == "__main__":
    main()

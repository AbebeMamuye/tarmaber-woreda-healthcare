import streamlit as st
import pandas as pd
import hashlib
import os
import base64
import plotly.express as px
import plotly.graph_objects as go
import socket
import sqlite3
from datetime import datetime
from st_supabase_connection import SupabaseConnection
from dotenv import load_dotenv

# Load .env if it exists
load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# LOGO HELPER
# ─────────────────────────────────────────────────────────────────────────────
def get_logo_b64() -> str:
    """Load the ICO logo and return a base64 data-URI string."""
    logo_path = os.path.join(os.path.dirname(__file__), 'abetechhealt_logo.ico')
    try:
        with open(logo_path, 'rb') as f:
            return 'data:image/x-icon;base64,' + base64.b64encode(f.read()).decode()
    except Exception:
        return ''

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Healthcare Performance Management System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS – hide ALL Streamlit branding & style the app
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* ── Hide ALL Streamlit branding ── */
[data-testid="stHeader"], 
[data-testid="stFooter"], 
[data-testid="stToolbar"], 
[data-testid="stDecoration"],
[data-testid="stSidebarHeader"],
[data-testid="stSidebarNav"],
[data-testid="stStatusWidget"],
[data-testid="stConnectionStatus"],
[data-testid="stManageAppButton"],
[data-testid="stViewerBadge"],
.stDeployButton,
.stAppDeployButton,
[class*="viewerBadge"],
[class*="stConnectionStatus"],
[class*="stStatusWidget"],
[class*="viewProfile"],
[class*="container_gzau3"],
/* Target buttons containing 'Manage app' text */
button:has(div:contains("Manage app")),
button:has(span:contains("Manage app")),
a[href*="share.streamlit.io/user/"],
#MainMenu, footer, header,
#Tabs-tab-list { 
    display: none !important; 
    visibility: hidden !important; 
    height: 0 !important; 
    width: 0 !important; 
    opacity: 0 !important; 
    pointer-events: none !important; 
}

/* ── App background ── */
.stApp { background: #f0f4f8 !important; }
.main .block-container { padding: 1.5rem 2rem 3rem 2rem !important; max-width: 100% !important; }
html, body, [class*="css"] { font-weight: 600 !important; }

/* Make all selectbox text and select dropdown text black */
div[data-baseweb="select"] {
    background-color: #ffffff !important;
    border-radius: 8px !important;
}
div[data-baseweb="select"] * {
    color: #000000 !important;
}
ul[role="listbox"] {
    background-color: #ffffff !important;
}
ul[role="listbox"] * {
    color: #000000 !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a1628 0%, #1a3a5c 100%) !important;
    border-right: 3px solid #1f77b4;
}
[data-testid="stSidebar"] label, 
[data-testid="stSidebar"] p, 
[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3, 
[data-testid="stSidebar"] span.stText { 
    color: #ffffff !important; 
    font-weight: 700 !important; 
}
[data-testid="stSidebar"] .stRadio > label { color: rgba(255,255,255,0.7) !important; font-size: 0.85rem !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.3) !important; border-width: 2px !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #1f77b4, #1565c0) !important;
    color: white !important; border: 2px solid #0a1628 !important;
    border-radius: 8px !important; font-weight: 800 !important;
    padding: 0.6rem 1.5rem !important; transition: all 0.25s ease !important;
    text-transform: uppercase; letter-spacing: 0.5px;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1565c0, #0d47a1) !important;
    transform: scale(1.02) !important;
    box-shadow: 0 4px 14px rgba(21,101,192,0.4) !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: white; border-radius: 12px;
    padding: 1.2rem; box-shadow: 0 4px 15px rgba(0,0,0,0.12);
    border: 3px solid #1f77b4 !important;
}
[data-testid="stMetricValue"] { font-weight: 900 !important; color: #0a1628 !important; }

/* ── Form inputs ── */
.stTextInput > div > div > input, .stNumberInput > div > div > input {
    border: 3px solid #0a1628 !important; border-radius: 8px !important;
    font-size: 1.05rem !important; font-weight: 800 !important;
    color: #0a1628 !important;
    padding: 10px 12px !important;
}
.stTextInput > div > div > input:focus, .stNumberInput > div > div > input:focus {
    border-color: #1f77b4 !important; background: #f0f7ff !important;
    box-shadow: 0 0 0 2px rgba(31, 119, 180, 0.2) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { gap: 10px; background: #cbd5e0; border-radius: 10px; padding: 6px; }
.stTabs [data-baseweb="tab"] {
    border-radius: 8px; padding: 10px 25px; font-weight: 800;
    background: #edf2f7; color: #2d3748 !important;
    border: 2px solid transparent !important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: white !important; color: #1f77b4 !important; border-color: #1f77b4 !important;
}

/* ── DataFrames ── */
.dataframe th { background: #1f77b4 !important; color: white !important; font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
WOREDAS = [
    'Debre Sina Health Center',
    'Armania Health Center',
    'Agamber Health Center',
    'Mezezo Health Center',
]

INDICATORS = [
    # Routine KPI (79 pts)
    {'col': 'wt',                 'label': 'WT',                   'max':  6.0, 'cat': 'Routine KPI'},
    {'col': 'rmh',                'label': 'RMH',                  'max': 10.0, 'cat': 'Routine KPI'},
    {'col': 'epi',                'label': 'EPI',                  'max':  3.0, 'cat': 'Routine KPI'},
    {'col': 'child_health',       'label': 'Child Health',         'max':  7.0, 'cat': 'Routine KPI'},
    {'col': 'nutrition',          'label': 'Nutrition',            'max':  4.0, 'cat': 'Routine KPI'},
    {'col': 'tb',                 'label': 'TB',                   'max':  5.0, 'cat': 'Routine KPI'},
    {'col': 'hiv',                'label': 'HIV',                  'max':  4.0, 'cat': 'Routine KPI'},
    {'col': 'msr',                'label': 'MSR',                  'max':  3.0, 'cat': 'Routine KPI'},
    {'col': 'medical_service',    'label': 'Medical Service',      'max':  5.0, 'cat': 'Routine KPI'},
    {'col': 'ncd',                'label': 'NCD',                  'max':  4.0, 'cat': 'Routine KPI'},
    {'col': 'hygiene',            'label': 'Hygiene',              'max':  5.0, 'cat': 'Routine KPI'},
    {'col': 'phem',               'label': 'PHEM',                 'max':  3.0, 'cat': 'Routine KPI'},
    {'col': 'pharmacy',           'label': 'Pharmacy',             'max':  4.0, 'cat': 'Routine KPI'},
    {'col': 'hmis',               'label': 'HMIS',                 'max':  4.0, 'cat': 'Routine KPI'},
    {'col': 'hr',                 'label': 'HR',                   'max':  1.0, 'cat': 'Routine KPI'},
    {'col': 'regulatory',         'label': 'Regulatory',           'max':  1.0, 'cat': 'Routine KPI'},
    {'col': 'hcf',                'label': 'HCF',                  'max': 10.0, 'cat': 'Routine KPI'},
    # Initiative (21 pts)
    {'col': 'full_emr',           'label': 'Full EMR',             'max':  3.0, 'cat': 'Initiative'},
    {'col': 'ultrasound',         'label': 'Ultrasound',           'max':  3.0, 'cat': 'Initiative'},
    {'col': 'apts',               'label': 'APTS',                 'max':  3.0, 'cat': 'Initiative'},
    {'col': 'community_pharmacy', 'label': 'Community Pharmacy',   'max':  3.0, 'cat': 'Initiative'},
    {'col': 'dm_test',            'label': 'DM Test',              'max':  3.0, 'cat': 'Initiative'},
    {'col': 'epi_modernization',  'label': 'EPI Modernization',    'max':  2.0, 'cat': 'Initiative'},
    {'col': 'zero_dose',          'label': 'Zero Dose',            'max':  2.0, 'cat': 'Initiative'},
    {'col': 'cash_program',       'label': 'Cash Program',         'max':  2.0, 'cat': 'Initiative'},
]

TOTAL_MAX = 100.0  # Latest: Routine KPI (79) + Initiative (21) = 100
INDICATOR_COUNT = len(INDICATORS)
IND_BY_COL = {i['col']: i for i in INDICATORS}

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'performance_data.xlsx')


# ─────────────────────────────────────────────────────────────────────────────
# AUTHENTICATION  (credentials kept in-code; only data goes to Excel)
# ─────────────────────────────────────────────────────────────────────────────
def _h(p): return hashlib.sha256(p.encode()).hexdigest()

# Each Dept Head has: 'cols' = list of indicator column keys they can enter
# IND_BY_COL maps column key → {col, label, max} from INDICATORS list
USERS = {
    # ── Admins ──────────────────────────────────────────────────────────────
    'admin':          {'ph': _h('admin@2018'),          'role': 'Admin',       'cols': [], 'dept_name': 'Administration'},
    'superadmin':     {'ph': _h('super@2024'),          'role': 'Super Admin', 'cols': [], 'dept_name': 'Administration'},
    # ── Department Heads (username / password / columns they enter) ─────────
    'medical':        {'ph': _h('Medical@2024'),        'role': 'Dept Head',
                       'cols': ['medical_service', 'ncd', 'wt', 'regulatory'],
                       'dept_name': 'Medical Service'},
    'pharmacy':       {'ph': _h('Pharmacy@2024'),       'role': 'Dept Head',
                       'cols': ['pharmacy', 'apts', 'community_pharmacy', 'ultrasound', 'dm_test'],
                       'dept_name': 'Pharmacy & Logistic'},
    'childhealth':    {'ph': _h('ChildHealth@2024'),    'role': 'Dept Head',
                       'cols': ['child_health', 'nutrition', 'epi', 'epi_modernization', 'zero_dose'],
                       'dept_name': 'Child Health'},
    'hmis':           {'ph': _h('hmis@2024'),           'role': 'Dept Head',
                       'cols': ['hmis', 'full_emr'],
                       'dept_name': 'HMIS'},
    'tb':             {'ph': _h('TB@2024'),             'role': 'Dept Head',
                       'cols': ['tb'],
                       'dept_name': 'TB & Leprosy'},
    'finance':        {'ph': _h('Finance@2024'),        'role': 'Dept Head',
                       'cols': ['hcf'],
                       'dept_name': 'Finance'},
    'cash_program':   {'ph': _h('CashProgram@2024'),    'role': 'Dept Head',
                       'cols': ['cash_program', 'hygiene'],
                       'dept_name': 'Cash Program'},
    'phem':           {'ph': _h('PHEM@2024'),           'role': 'Dept Head',
                       'cols': ['phem'],
                       'dept_name': 'PHEM'},
    'multi_sectoral': {'ph': _h('MultiSectoral@2024'), 'role': 'Dept Head',
                       'cols': ['msr', 'hiv'],
                       'dept_name': 'Multi-Sectoral & HIV'},
    'rmh':            {'ph': _h('rmh@2024'),            'role': 'Dept Head',
                       'cols': ['rmh'],
                       'dept_name': 'RMH'},
    'hr':             {'ph': _h('HR@2024'),             'role': 'Dept Head',
                       'cols': ['hr'],
                       'dept_name': 'HR Department'},
}


def verify_user(username: str, password: str):
    u = USERS.get(username.strip().lower())
    if u and u['ph'] == _h(password.strip()):
        return u
    return None


# ─────────────────────────────────────────────────────────────────────────────
# DATA LAYER (Supabase Cloud Storage)
# ─────────────────────────────────────────────────────────────────────────────
QUARTERS = [
    "-- Select Quarter --",
    "Quarter 1",
    "Quarter 2",
    "Quarter 3",
    "Quarter 4"
]
YEARS = [
    "-- Select Year --",
    "2016",
    "2017",
    "2018",
    "2019",
    "2020",
    "2021"
]

def get_db_connection():
    """Get Supabase connection with credentials provided by the user."""
    # Priority: st.secrets -> .env -> Hardcoded fallback
    try:
        url = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL") or "https://etmvricanlatzhrwlsvx.supabase.co"
        key = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY") or "sb_publishable_b1RPpHyaAA2_kXhiFame1A_O41Ds3IE"
    except Exception:
        url = os.getenv("SUPABASE_URL") or "https://etmvricanlatzhrwlsvx.supabase.co"
        key = os.getenv("SUPABASE_KEY") or "sb_publishable_b1RPpHyaAA2_kXhiFame1A_O41Ds3IE"

    try:
        return st.connection("supabase", type=SupabaseConnection, 
                             url=url, key=key)
    except Exception as e:
        print(f"Supabase Connection Error: {e}")
        return None

def execute_query(table, query_type="select", data=None, filters=None):
    """Abstraction for Supabase operations."""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        if query_type == "select":
            res = conn.table(table).select("*").execute()
            if res.data:
                return pd.DataFrame(res.data)
            return pd.DataFrame()
        elif query_type == "upsert":
            res = conn.table(table).upsert(data, on_conflict="woreda_name,year,quarter").execute()
            return True
    except Exception as e:
        print(f"Query Error ({query_type}): {e}")
        return None

def recalculate(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty: return df
    cols = [i['col'] for i in INDICATORS if i['col'] in df.columns]
    # Ensure all indicator columns are numeric
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0.0)
    
    df['total_score'] = df[cols].sum(axis=1).round(2)
    
    # Weighted achievement percentage (out of TOTAL_MAX)
    overall_percentage = (df['total_score'] / TOTAL_MAX * 100).round(2)
    df['avg_indicator_perf'] = overall_percentage
    df['percentage'] = overall_percentage
    return df

def cleanup_df(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize dataframe structure, ensuring all required columns exist."""
    # 1. Ensure core columns exist
    for c in ['woreda_name', 'year', 'quarter']:
        if c not in df.columns:
            df[c] = ""
    
    # 2. Standardize core column types
    df['woreda_name'] = df['woreda_name'].astype(str).str.strip()
    df['year']        = df['year'].astype(str).str.strip()
    df['quarter']     = df['quarter'].astype(str).str.strip()
    
    # 3. Add missing indicators and FORCE float64 dtype
    for ind in INDICATORS:
        if ind['col'] not in df.columns:
            df[ind['col']] = pd.array([0.0] * len(df), dtype='float64')
        else:
            df[ind['col']] = pd.to_numeric(df[ind['col']], errors='coerce').fillna(0.0).astype('float64')
    
    # 4. Add summary numeric columns, force float64
    for c in ('total_score', 'percentage', 'avg_indicator_perf'):
        if c not in df.columns:
            df[c] = pd.array([0.0] * len(df), dtype='float64')
        else:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0.0).astype('float64')
    
    # 5. last_updated must stay string
    if 'last_updated' not in df.columns:
        df['last_updated'] = ''
    df['last_updated'] = df['last_updated'].fillna('').astype(str)
    
    return df

def init_db():
    """Initial load if database is empty."""
    rows = []
    for year in YEARS:
        if year.startswith("--"): continue
        for q in QUARTERS:
            if q.startswith("--"): continue
            for w in WOREDAS:
                row = {'woreda_name': w, 'year': year, 'quarter': q}
                for ind in INDICATORS:
                    row[ind['col']] = 0.0
                row['total_score'] = 0.0
                row['percentage'] = 0.0
                row['avg_indicator_perf'] = 0.0
                row['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                rows.append(row)
    df = pd.DataFrame(rows)
    save_data(df)
    return df

def load_data() -> pd.DataFrame:
    conn = get_db_connection()
    
    # Handle Paused/Offline State by attempting local fallback
    if conn is None or conn == "PAUSED":
        st.info("🔄 **Local Mode:** Attempting to load data from local backup...")
        try:
            # Try Excel first
            if os.path.exists(DATA_FILE):
                df_excel = pd.read_excel(DATA_FILE)
                df_excel = cleanup_df(df_excel)
                df_excel = df_excel[df_excel['woreda_name'].isin(WOREDAS)].copy()
                if not df_excel.empty:
                    return df_excel
            # Try Local DB
            local_db = os.path.join(os.path.dirname(__file__), 'healthcare_performance.db')
            if os.path.exists(local_db):
                sqlite_conn = sqlite3.connect(local_db)
                df = pd.read_sql_query("SELECT * FROM performance_data", sqlite_conn)
                sqlite_conn.close()
                if 'id' in df.columns: df = df.drop(columns=['id'])
                df = cleanup_df(df)
                df = df[df['woreda_name'].isin(WOREDAS)].copy()
                if not df.empty: return df
        except Exception as e:
            st.error(f"Failed to load local backup: {e}")
            
        st.warning("⚠️ No database connection. Showing empty dashboard.")
        # Return skeleton when offline and empty
        skeleton_rows = []
        for year in YEARS:
            if year.startswith("--"): continue
            for q in QUARTERS:
                if q.startswith("--"): continue
                for w in WOREDAS:
                    row = {'woreda_name': w, 'year': year, 'quarter': q}
                    for ind in INDICATORS:
                        row[ind['col']] = 0.0
                    row['total_score'] = 0.0
                    row['percentage'] = 0.0
                    row['avg_indicator_perf'] = 0.0
                    row['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                    skeleton_rows.append(row)
        return pd.DataFrame(skeleton_rows)
    
    try:
        # Try to fetch from table 'performance_data'
        res = conn.table("performance_data").select("*").execute()
        if not res.data or len(res.data) == 0:
            return init_db()
        
        df = pd.DataFrame(res.data)
        
        # If the resulting DataFrame has a RangeIndex (integer columns), something is wrong.
        if isinstance(df.columns, pd.RangeIndex):
             st.error("⚠️ Loaded data is malformed (missing headers). Reverting to default view.")
             return pd.DataFrame(columns=['woreda_name', 'year', 'quarter'] + [i['col'] for i in INDICATORS])

        if 'id' in df.columns:
            df = df.drop(columns=['id'])
            
        df = cleanup_df(df)
        df = df[df['woreda_name'].isin(WOREDAS)].copy()
        if df.empty:
            return init_db()
        return df
    except Exception as e:
        err_msg = str(e)
        if "Name or service not known" in err_msg or "getaddrinfo failed" in err_msg:
            st.error("❌ **Database Paused:** The connection to Supabase failed (DNS error). Please resume your project in the Supabase dashboard.")
        elif "521" in err_msg or "Web server is down" in err_msg or "JSON could not be generated" in err_msg:
            st.error("❌ **Database Starting Up (Error 521):** The Supabase server is not yet responding. This usually happens if the project was just resumed and is still booting up.")
            st.warning("⏳ **Action:** Please wait 2-3 minutes and refresh this page. If it persists, ensure your project is actively 'Running' in Supabase.")
        else:
            st.error(f"❌ Database error: {e}")
        # ALWAYS return a skeleton to avoid KeyError later
        return pd.DataFrame(columns=['woreda_name', 'year', 'quarter'] + [i['col'] for i in INDICATORS])

def save_data(df: pd.DataFrame, year=None, quarter=None):
    # Recalculate totals before saving
    df = recalculate(df)
    
    # 1. Save to Local Excel Backup
    try:
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        df.to_excel(DATA_FILE, index=False)
    except Exception as e:
        print(f"Failed to save local Excel backup: {e}")
        
    # 2. Save to Local SQLite Backup
    try:
        local_db = os.path.join(os.path.dirname(__file__), 'healthcare_performance.db')
        sqlite_conn = sqlite3.connect(local_db)
        df.to_sql("performance_data", sqlite_conn, if_exists="replace", index=False)
        sqlite_conn.close()
    except Exception as e:
        print(f"Failed to save local SQLite backup: {e}")

    # 3. Save to Supabase Cloud
    conn = get_db_connection()
    if conn is None or conn == "PAUSED":
        st.warning("⚠️ **Saved to Local Backup:** Cloud database is currently offline or paused. Your changes are saved locally.")
        return
    
    # Only upload the rows for the selected evaluation period to speed up network latency
    if year and quarter:
        sync_df = df[(df['year'] == year) & (df['quarter'] == quarter)]
    else:
        sync_df = df
        
    # Convert to list of dicts for Supabase
    records = sync_df.to_dict('records')
    
    try:
        # Upsert based on natural primary key (woreda, year, quarter)
        conn.table("performance_data").upsert(records, on_conflict="woreda_name,year,quarter").execute()
    except Exception as e:
        st.error(f"Failed to sync data to cloud: {e}")
        st.warning("⚠️ **Note:** Your changes were saved locally, but could not sync to cloud.")

def init_data_file():
    """No-op for compatibility with other parts of the script."""
    pass

# ─────────────────────────────────────────────────────────────────────────────
# UI HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def perf_band(pct):
    """Return (hex_color, emoji, label) based on percentage."""
    if pct >= 75:   return '#28a745', '🟢', 'High'
    elif pct >= 50: return '#ffc107', '🟡', 'Average'
    else:           return '#dc3545', '🔴', 'Low'


def page_header(title: str, subtitle: str = ''):
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0a1628 0%,#1f77b4 100%);
                padding:22px 30px;border-radius:14px;margin-bottom:24px;
                box-shadow:0 6px 24px rgba(0,0,0,0.22);">
        <h1 style="color:white;margin:0 0 4px 0;font-size:1.75rem;font-weight:800;">{title}</h1>
        <p style="color:rgba(255,255,255,0.75);margin:0;font-size:0.9rem;">{subtitle}</p>
    </div>""", unsafe_allow_html=True)


def card(content_html: str, padding='20px'):
    st.markdown(f"""
    <div style="background:white;border-radius:12px;padding:{padding};
                box-shadow:0 2px 12px rgba(0,0,0,0.07);margin-bottom:16px;">
        {content_html}
    </div>""", unsafe_allow_html=True)


def footer():
    st.markdown("""
    <div style="text-align:center;padding:30px 0 10px;border-top:1px solid #e2e8f0;margin-top:40px;">
        <p style="color:#a0aec0;font-size:0.82rem;margin:3px 0;">
            © 2026 All Rights Reserved &nbsp;|&nbsp;
            Developed by <strong style="color:#1f77b4;">Abe_Technology</strong>
        </p>
        <p style="color:#cbd5e0;font-size:0.78rem;margin:3px 0;">
            <a href="https://t.me/AI_Technology" style="color:#1f77b4;text-decoration:none;">@AI_Technology</a>
        </p>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# LOGIN PAGE
# ─────────────────────────────────────────────────────────────────────────────
def login_page():
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg,#0a1628 0%,#1a3a5c 50%,#0a1628 100%) !important; }
    </style>""", unsafe_allow_html=True)

    # Scrolling marquee — single text, 2× font size, bold, native <marquee>
    st.markdown("""
    <div style="background:rgba(255,255,255,0.10);border-radius:10px;
                padding:12px 0;margin-bottom:32px;overflow:hidden;">
        <marquee behavior="scroll" direction="left" scrollamount="8"
                 style="color:white;font-weight:900;font-size:1.8rem;
                        letter-spacing:0.5px;font-family:'Inter',sans-serif;">
            &nbsp;&nbsp;&nbsp; Healthcare Performance Management System — Tarmaber Woreda Health Office
        </marquee>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.1, 1])
    with col:
        logo_b64 = get_logo_b64()
        logo_html = (
            f'<img src="{logo_b64}" style="width:90px;height:90px;object-fit:contain;'
            f'border-radius:12px;box-shadow:0 4px 16px rgba(0,0,0,0.18);margin-bottom:12px;" />'
            if logo_b64 else '<div style="font-size:3.2rem;">🏥</div>'
        )
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.97);border-radius:20px;padding:42px 38px;
                    box-shadow:0 24px 64px rgba(0,0,0,0.35);">
            <div style="text-align:center;margin-bottom:28px;">
                {logo_html}
                <h2 style="color:#0a1628;margin:10px 0 4px;font-weight:800;font-size:1.6rem;">Welcome Back</h2>
                <p style="color:#718096;margin:0;font-size:0.88rem;">Healthcare Performance Management System</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("🔐  Sign In", use_container_width=True)

        if submitted:
            if not username or not password:
                st.error("⚠️ Please enter both username and password.")
            else:
                user = verify_user(username, password)
                if user:
                    import hashlib
                    st.session_state.authenticated = True
                    st.session_state.username  = username.strip().lower()
                    st.session_state.role      = user['role']
                    st.session_state.u_cols    = user.get('cols', [])      # list of col keys
                    st.session_state.u_dept    = user.get('dept_name', '')
                    st.session_state.view      = 'Data Entry' if user['role'] == 'Dept Head' else 'Dashboard'
                    # Store login credentials hash in query parameters to persist session
                    auth_token = hashlib.sha256(f"{username.strip().lower()}:{user['ph']}".encode()).hexdigest()
                    st.query_params["u"] = username.strip().lower()
                    st.query_params["t"] = auth_token
                    # Set defaults
                    st.session_state.filter_year = "-- Select Year --"
                    st.session_state.filter_quarter = "-- Select Quarter --"
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password.")

    st.markdown("""
    <div style="text-align:center;padding-top:28px;">
        <p style="color:rgba(255,255,255,0.5);font-size:0.82rem;margin:3px 0;">
            © 2026 All Rights Reserved &nbsp;|&nbsp;
            Developed by <strong style="color:#64b5f6;">Abe_Technology</strong> &nbsp;|&nbsp;
            <a href="https://t.me/AI_Technology" style="color:#64b5f6;text-decoration:none;">@AI_Technology</a>
        </p>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
def render_sidebar():
    role     = st.session_state.role
    username = st.session_state.username

    role_color = {'Admin': '#1f77b4', 'Super Admin': '#7c3aed', 'Dept Head': '#28a745'}.get(role, '#718096')

    with st.sidebar:
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.1);border-radius:12px;padding:16px;
                    margin-bottom:18px;border:1px solid rgba(255,255,255,0.18);">
            <div style="display:flex;align-items:center;gap:12px;">
                <div style="width:46px;height:46px;border-radius:50%;background:{role_color};
                            display:flex;align-items:center;justify-content:center;
                            font-size:1.3rem;font-weight:800;color:white;flex-shrink:0;">
                    {username[0].upper()}
                </div>
                <div>
                    <p style="margin:0;font-weight:700;color:white;font-size:0.95rem;">{username}</p>
                    <p style="margin:2px 0 0;font-size:0.76rem;color:rgba(255,255,255,0.65);">{role}</p>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("---")

        if role in ['Admin', 'Super Admin']:
            st.markdown("""
            <div style="color:rgba(255,255,255,0.6);font-size:0.7rem;font-weight:700;
                        text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;">
                📅 Global Filters
            </div>""", unsafe_allow_html=True)
            
            y_idx = YEARS.index(st.session_state.filter_year) if st.session_state.filter_year in YEARS else 0
            st.session_state.filter_year = st.selectbox("Year (EFY)", YEARS, index=y_idx)
            
            q_idx = QUARTERS.index(st.session_state.filter_quarter) if st.session_state.filter_quarter in QUARTERS else 0
            st.session_state.filter_quarter = st.selectbox("Quarter", QUARTERS, index=q_idx)
            
            st.markdown("---")

        if role == 'Dept Head':
            dept_name = st.session_state.u_dept
            cols      = st.session_state.u_cols
            elements  = ', '.join(IND_BY_COL[c]['label'] for c in cols if c in IND_BY_COL)
            st.markdown(f"""
            <div style="background:rgba(40,167,69,0.18);border:1px solid rgba(40,167,69,0.4);
                        border-radius:8px;padding:12px 14px;margin-bottom:14px;">
                <p style="color:rgba(255,255,255,0.9);margin:0 0 3px;font-size:0.82rem;font-weight:600;">
                    📊 Department
                </p>
                <p style="color:white;margin:0;font-weight:700;font-size:0.95rem;">{dept_name}</p>
                <p style="color:rgba(255,255,255,0.55);margin:4px 0 0;font-size:0.74rem;">
                    {len(cols)} data element(s): {elements}
                </p>
            </div>""", unsafe_allow_html=True)
            st.session_state.view = 'Data Entry'

        elif role == 'Admin':
            st.session_state.view = 'Dashboard' # Always dashboard

        elif role == 'Super Admin':
            nav_opts = ['Dashboard', 'Edit Data']
            cur = st.session_state.get('view', 'Dashboard')
            idx = nav_opts.index(cur) if cur in nav_opts else 0
            chosen = st.radio("📌 Navigation", nav_opts, index=idx)
            st.session_state.view = chosen

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.query_params.clear()
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# DEPARTMENT HEAD — Data Entry
# ─────────────────────────────────────────────────────────────────────────────
def dept_head_view():
    """Data entry view for Dept Head — supports 1 or many data elements via dropdown."""
    cols      = st.session_state.u_cols      # list of column keys
    dept_name = st.session_state.u_dept
    username  = st.session_state.username

    page_header(f"📝 {dept_name} — Data Entry",
                f"Logged in as: {username}  |  Department: {dept_name}")

    df = load_data()
    if df is None or not isinstance(df, pd.DataFrame) or 'woreda_name' not in df.columns:
        st.error("❌ Data structure is invalid. Please contact the administrator.")
        return

    # ── BLINKING NOTICE ───────────────────────────────────────────────────────
    st.markdown("""
    <style>
    @keyframes blink-border {
        0%,100% { box-shadow: 0 0 0px 0px rgba(220,53,69,0); border-color:#dc3545; }
        50%      { box-shadow: 0 0 18px 6px rgba(220,53,69,0.55); border-color:#ff8c00; }
    }
    @keyframes blink-text {
        0%,100% { opacity: 1; }
        50%      { opacity: 0.35; }
    }
    .entry-notice {
        display:flex; align-items:center; gap:14px;
        background:linear-gradient(135deg,#fff3cd,#ffe0e0);
        border:3px solid #dc3545; border-radius:12px;
        padding:14px 22px; margin-bottom:22px;
        animation: blink-border 1.2s ease-in-out infinite;
    }
    .entry-notice-icon { font-size:2rem; flex-shrink:0; }
    .entry-notice-text {
        color:#8b0000; font-weight:900; font-size:1.05rem;
        text-transform:uppercase; letter-spacing:0.8px;
        animation: blink-text 1.2s ease-in-out infinite;
    }
    </style>
    <div class="entry-notice">
        <span class="entry-notice-icon">⚠️</span>
        <span class="entry-notice-text">YOU SHOULD ENTER DATA FROM 100%</span>
    </div>
    """, unsafe_allow_html=True)

    # ── PERIOD SELECTION ──────────────────────────────────────────────────────
    st.markdown("""
    <div style="background:#f8fafc; border:2px solid #1f77b4; border-radius:12px; padding:15px; margin-bottom:20px;">
        <p style="color:#1a3a5c; font-weight:800; font-size:0.9rem; margin-bottom:10px; text-transform:uppercase;">
            📅 Select Evaluation Period:
        </p>
    </div>""", unsafe_allow_html=True)
    per_c1, per_c2 = st.columns(2)
    with per_c1:
        y_idx = YEARS.index(st.session_state.get('filter_year', "-- Select Year --")) if st.session_state.get('filter_year') in YEARS else 0
        sel_year = st.selectbox("Year (EFY)", YEARS, index=y_idx, key="filter_year")
    with per_c2:
        q_idx = QUARTERS.index(st.session_state.get('filter_quarter', "-- Select Quarter --")) if st.session_state.get('filter_quarter') in QUARTERS else 0
        sel_q = st.selectbox("Quarter", QUARTERS, index=q_idx, key="filter_quarter")

    if sel_year.startswith("--") or sel_q.startswith("--"):
        st.info("ℹ️ Please select **Year** and **Quarter** to view and edit performance data.")
        return


    # ── DROPDOWN: pick which data element to enter (shown only if >1 element) ──
    if len(cols) > 1:
        # Build readable options list
        options = [IND_BY_COL[c]['label'] for c in cols if c in IND_BY_COL]
        st.markdown("""
        <div style="background:white;border-radius:12px;padding:18px 22px;
                    box-shadow:0 2px 12px rgba(0,0,0,0.07);margin-bottom:20px;">
            <p style="color:#2d3748;font-weight:700;font-size:1rem;margin:0 0 10px;">
                🎯 Select Data Element to Enter:
            </p>
        </div>""", unsafe_allow_html=True)
        chosen_label = st.selectbox(
            "Data Element",
            options=options,
            key="dept_element_select",
            label_visibility="collapsed"
        )
        # Map label back to col key
        col_key = next(c for c in cols if c in IND_BY_COL and IND_BY_COL[c]['label'] == chosen_label)
    else:
        col_key = cols[0]
        chosen_label = IND_BY_COL[col_key]['label'] if col_key in IND_BY_COL else col_key

    col_label = IND_BY_COL[col_key]['label'] if col_key in IND_BY_COL else col_key
    col_max   = float(IND_BY_COL[col_key]['max']) if col_key in IND_BY_COL else 5.0

    # ── ELEMENT BADGE ─────────────────────────────────────────────────────────
    badge_items = []
    for c in cols:
        if c not in IND_BY_COL: continue
        is_active = (c == col_key)
        bg = "#1f77b4" if is_active else "#e2e8f0"
        color = "white" if is_active else "#4a5568"
        icon = "✔ " if is_active else ""
        label = IND_BY_COL[c]["label"]
        item = f'<span style="background:{bg}; color:{color}; padding:4px 12px; border-radius:20px; font-size:0.8rem; font-weight:600; margin:2px;">{icon}{label}</span>'
        badge_items.append(item)
    badge_list = " ".join(badge_items)
    st.markdown(f"""
    <div style="background:white;border-radius:10px;padding:14px 20px;
                box-shadow:0 2px 10px rgba(0,0,0,0.06);margin-bottom:18px;
                border-left:4px solid #1f77b4;">
        <span style="color:#718096;font-size:0.8rem;font-weight:600;
                     text-transform:uppercase;letter-spacing:0.5px;">Available Elements:</span><br>
        <div style="margin-top:8px;">{badge_list}</div>
    </div>""", unsafe_allow_html=True)

    # ── ENTRY CARD ────────────────────────────────────────────────────────────
    card(f"""
    <h3 style="color:#2d3748;margin:0 0 6px;">Enter <span style="color:#1f77b4;">{col_label}</span> Scores</h3>
    <p style="color:#718096;margin:0;font-size:0.88rem;">
        Values: 0 – 100% per Health Center. (Cut-point equivalent out of {col_max} will be computed automatically). Click <strong>Save</strong> when done.
    </p>""")

    # Build current values from DB (Filtered by Year & Quarter)
    current_vals = {}
    for w in WOREDAS:
        mask = (df['woreda_name'] == w) & (df['year'] == sel_year) & (df['quarter'] == sel_q)
        row = df[mask]
        weighted_val = float(row[col_key].iloc[0]) if not row.empty else 0.0
        # Convert to percentage out of 100 for display
        current_vals[w] = (weighted_val * 100.0 / col_max) if col_max > 0 else 0.0

    with st.form(f"dept_form_{col_key}_{sel_year}_{sel_q}"):
        # Table header - BOLD BORDERS
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:3fr 2fr;gap:0;
                    background:linear-gradient(135deg,#0a1628,#1f77b4);
                    border:3px solid #0a1628;
                    border-radius:12px 12px 0 0;padding:12px 20px;">
            <div style="color:white;font-weight:900;font-size:1.1rem;letter-spacing:0.5px;">🏘️ HEALTH CENTER NAME</div>
            <div style="color:white;font-weight:900;font-size:1.1rem;text-align:center;letter-spacing:0.5px;">
                {col_label.upper()}&nbsp;<span style="opacity:0.8;font-weight:400;font-size:0.85rem;">(ENTER OUT OF 100, MAX CUT POINT: {col_max})</span>
            </div>
        </div>""", unsafe_allow_html=True)

        inputs = {}
        for i, woreda in enumerate(WOREDAS):
            bg = '#f8fafc' if i % 2 == 0 else '#ffffff'
            c_name, c_inp = st.columns([3, 2])
            with c_name:
                st.markdown(f"""
                <div style="background:{bg};padding:10px 20px;border-bottom:2px solid #cbd5e0;
                            border-left:6px solid #1f77b4;border-right:2px solid #cbd5e0;
                            min-height:58px;display:flex;align-items:center;">
                    <span style="color:#1a3a5c;font-size:0.85rem;font-weight:900;margin-right:12px;">{i+1:02d}</span>
                    <span style="color:#0a1628;font-weight:800;font-size:1rem;">{woreda.upper()}</span>
                </div>""", unsafe_allow_html=True)
            with c_inp:
                st.markdown(f'<div style="background:{bg};border-bottom:2px solid #cbd5e0;border-right:2px solid #cbd5e0;border-left:2px solid #cbd5e0;padding:4px 8px;min-height:58px;display:flex;flex-direction:column;justify-content:center;">', unsafe_allow_html=True)
                raw_val = st.number_input(
                    f"s{i}", min_value=0.0, max_value=None,
                    value=min(current_vals[woreda], 100.0), step=1.0,
                    key=f"di_{col_key}_{i}", label_visibility="collapsed")
                inputs[woreda] = raw_val
                if raw_val > 100.0:
                    st.markdown('<p style="color:#e53e3e; font-size:0.8rem; font-weight:700; margin:4px 0 0 0;">Please Enter value <=100</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        total_inp = sum(inputs.values())
        average   = total_inp / len(WOREDAS)

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#e0f2fe,#bae6fd);
                    border:3px solid #0c4a6e;
                    border-radius:0 0 12px 12px;padding:16px 20px;margin-bottom:20px;">
            <span style="color:#0c4a6e;font-weight:900;font-size:1.1rem;">
                📊 TOTAL: <span style="font-size:1.3rem;">{total_inp:.1f}%</span>
                &nbsp;&nbsp;|&nbsp;&nbsp; AVERAGE: <span style="font-size:1.3rem;">{average:.2f}%</span>
            </span>
        </div>""", unsafe_allow_html=True)

        any_invalid = any(val > 100.0 for val in inputs.values())

        _, btn_col, _ = st.columns([1, 2, 1])
        with btn_col:
            save = st.form_submit_button(
                f"💾  Save {col_label} Data", 
                use_container_width=True, 
                type="primary"
            )

    if save:
        if any_invalid:
            st.error("⚠️ Cannot save data. Some values are greater than 100%. Please correct them and try again.")
        else:
            ts = datetime.now().strftime('%Y-%m-%d %H:%M')
            for woreda, val in inputs.items():
                weighted_val = float((val * col_max) / 100.0)
                mask = (df['woreda_name'] == woreda) & (df['year'] == sel_year) & (df['quarter'] == sel_q)
                if mask.any():
                    # Use .at[] row-by-row to avoid pandas dtype coercion errors
                    for idx in df.index[mask]:
                        df.at[idx, col_key]       = weighted_val
                        df.at[idx, 'last_updated'] = ts
                else:
                    new_row = {'woreda_name': woreda, 'year': sel_year, 'quarter': sel_q, col_key: weighted_val}
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
            save_data(df, year=sel_year, quarter=sel_q)
            st.session_state.success_msg = f"✅ {col_label} data saved for {sel_year} {sel_q}!"
            st.session_state.show_balloons = True
            st.rerun()

    # ── Summary table (HTML for BOLD BORDERS) ─────────────────────────────────
    st.markdown("---")
    st.markdown(f"### 📋 Current {col_label} Values")
    
    st.markdown("""
    <style>
    .sumtable {
        width: 100%; border-collapse: collapse; border: 4px solid #000000;
        border-radius: 10px; overflow: hidden; margin-bottom: 30px;
    }
    .sumtable th {
        background: #0a1628; color: white; padding: 12px; font-weight: 900;
        border: 2px solid #ffffff; text-align: center;
    }
    .sumtable td {
        padding: 10px 12px; border: 2px solid #000000; font-weight: 800;
        color: #000000; text-align: center;
    }
    .sumtable tr:nth-child(even) { background: #f8fafc; }
    </style>""", unsafe_allow_html=True)

    header = ['#', 'HEALTH CENTER', f'{col_label.upper()} SCORE', 'PERCENTAGE', 'LEVEL']
    html = '<table class="sumtable"><thead><tr>'
    for h in header: html += f'<th>{h}</th>'
    html += '</tr></thead><tbody>'

    for i, w in enumerate(WOREDAS):
        mask = (df['woreda_name'] == w) & (df['year'] == sel_year) & (df['quarter'] == sel_q)
        row = df[mask]
        v   = float(row[col_key].iloc[0]) if not row.empty else 0.0
        pct = v / col_max * 100 if col_max else 0
        color, emoji, lvl = perf_band(pct)
        html += f'<tr>'
        html += f'<td>{i+1}</td>'
        html += f'<td style="text-align:left; background:#e2e8f0;">{w}</td>'
        html += f'<td>{v:.1f}</td>'
        html += f'<td style="color:{color};">{pct:.1f}% {emoji}</td>'
        html += f'<td><span style="background:{color}; color:white; padding:2px 8px; border-radius:4px;">{lvl}</span></td>'
        html += '</tr>'
    
    html += '</tbody></table>'
    st.markdown(html, unsafe_allow_html=True)
    footer()


# ─────────────────────────────────────────────────────────────────────────────
# RANKING TABLE  (HTML, clean)
# ─────────────────────────────────────────────────────────────────────────────
def render_ranking_table(ranked: pd.DataFrame):
    st.markdown("""
    <style>
    .rtable {
        width: 100%;
        border-collapse: collapse;
        border: 4px solid #000000;
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
        font-size: 0.95rem;
    }
    .rtable thead tr { background: linear-gradient(135deg, #0a1628, #1f77b4); }
    .rtable th {
        color: white;
        padding: 16px 20px;
        text-align: left;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 1px;
        border: 2px solid #ffffff;
    }
    .rtable td {
        padding: 14px 20px;
        border: 2px solid #000000; /* BOLD ALL BORDERS */
        color: #000000;
        font-weight: 800;
    }
    .rtable tbody tr:hover td { background: #edf2f7 !important; }
    </style>""", unsafe_allow_html=True)

    rows_html = ""
    for _, row in ranked.iterrows():
        rank  = int(row['rank'])
        wr    = row['woreda_name']
        total = row['total_score']
        # Use Average Indicator Performance for the rankings
        pct   = row['avg_indicator_perf']
        color, emoji, lvl = perf_band(pct)
        bg    = '#ffffff' if rank % 2 == 0 else '#f8fafc'
        w_bar = min(int(pct), 100)

        if rank == 1:   badge_style = "background:#FFD700;color:#333;"
        elif rank == 2: badge_style = "background:#C0C0C0;color:#333;"
        elif rank == 3: badge_style = "background:#CD7F32;color:white;"
        else:           badge_style = f"background:{color};color:white;"

        rank_text = {1: '🥇', 2: '🥈', 3: '🥉'}.get(rank, f'#{rank}')

        rows_html += f"""
        <tr style="background:{bg};">
            <td style="text-align:center;">
                <span style="{badge_style}display:inline-flex;align-items:center;justify-content:center;
                             width:36px;height:36px;border-radius:50%;font-weight:800;font-size:0.82rem;">
                    {rank_text}
                </span>
            </td>
            <td style="font-weight:600;color:#2d3748;">{wr}</td>
            <td style="text-align:center;font-weight:700;color:#1f77b4;font-size:1rem;">
                {total:.1f}
                <span style="color:#a0aec0;font-weight:400;font-size:0.78rem;">/ {TOTAL_MAX:.0f}</span>
            </td>
            <td style="min-width:220px;">
                <div style="display:flex;align-items:center;gap:10px;">
                    <div style="flex:1;background:#e2e8f0;border-radius:4px;height:10px;overflow:hidden;">
                        <div style="width:{w_bar}%;background:{color};height:100%;border-radius:4px;"></div>
                    </div>
                    <span style="font-weight:800;color:{color};min-width:68px;text-align:right;font-size:0.95rem;">
                        {pct:.1f}% {emoji}
                    </span>
                </div>
            </td>
            <td style="text-align:center;">
                <span style="background:{color}22;color:{color};border:1px solid {color};
                             padding:3px 12px;border-radius:12px;font-size:0.78rem;font-weight:700;">
                    {lvl}
                </span>
            </td>
        </tr>"""

    st.markdown(f"""
    <table class="rtable">
        <thead>
            <tr>
                <th style="width:60px;text-align:center;">Rank</th>
                <th>Health Center Name</th>
                <th style="text-align:center;">Total Score</th>
                <th>Performance</th>
                <th style="text-align:center;">Level</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>
    <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:14px;">
        <span style="background:#28a74522;color:#28a745;border:1px solid #28a745;
                     padding:4px 12px;border-radius:12px;font-size:0.78rem;font-weight:600;">🟢 High ≥75%</span>
        <span style="background:#ffc10722;color:#856404;border:1px solid #ffc107;
                     padding:4px 12px;border-radius:12px;font-size:0.78rem;font-weight:600;">🟡 Average 50–74%</span>
        <span style="background:#dc354522;color:#dc3545;border:1px solid #dc3545;
                     padding:4px 12px;border-radius:12px;font-size:0.78rem;font-weight:600;">🔴 Low &lt;50%</span>
    </div><br>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# CHARTS
# ─────────────────────────────────────────────────────────────────────────────
def render_charts(ranked: pd.DataFrame, df: pd.DataFrame):
    # ── CHART 1: Woreda Ranking Bar Chart ─────────────────────────────────────
    # Color coding logic: >=75 green, >=50 yellow, <50 red
    def map_bar_color(val):
        if val >= 75: return '#28a745'
        if val >= 50: return '#ffc107'
        return '#dc3545'
    
    ranked_plot = ranked.copy()
    ranked_plot['bar_color'] = ranked_plot['avg_indicator_perf'].apply(map_bar_color)

    bar = px.bar(
        ranked_plot, x='avg_indicator_perf', y='woreda_name', orientation='h',
        color='bar_color',
        color_discrete_map={'#28a745': '#28a745', '#ffc107': '#ffc107', '#dc3545': '#dc3545'},
        text='avg_indicator_perf',
        labels={'avg_indicator_perf': 'Avg Performance (%)', 'woreda_name': 'Health Center'},
        title='<b>Health Center Performance Rankings (Average Indicator Achievement)</b>',
    )
    bar.update_layout(
        height=620, showlegend=False, paper_bgcolor='white', plot_bgcolor='#f8fafc',
        xaxis=dict(range=[0, 105], title='Average Performance (%)'),
        yaxis=dict(categoryorder='total ascending', title=''),
        margin=dict(l=8, r=80, t=48, b=16),
    )
    bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside',
                      textfont=dict(size=11, color='#000'))
    st.plotly_chart(bar, use_container_width=True)

    st.markdown("---")  # Separator

    # ── CHART 2: Detailed Line Graph ──────────────────────────────────────────
    st.markdown("""
    <div style="background:#f8fafc; border:4px solid #1f77b4; border-radius:10px; padding:16px; margin-bottom:15px; border-left: 10px solid #1f77b4;">
        <p style="color:#0a1628; font-weight:900; font-size:1.1rem; margin:0; text-transform:uppercase; letter-spacing:0.5px;">
            📊 Performance Breakdown — Indicator Level Analysis
        </p>
    </div>""", unsafe_allow_html=True)
    
    selected_woreda = st.selectbox(
        "🏘️ Select Health Center to Analyze Individual Indicators:", 
        options=sorted(WOREDAS), 
        index=0 if not ranked.empty else 0
    )
    
    if not selected_woreda:
        st.info("💡 Please select a Health Center to generate the indicator breakdown graph.")
    else:
        # Prepare data for line chart
        plot_data = []
        w_row = df[df['woreda_name'] == selected_woreda]
        if not w_row.empty:
            for ind in INDICATORS:
                plot_data.append({
                    'Woreda': selected_woreda,
                    'Indicator': ind['label'],
                    'Score': float(w_row[ind['col']].iloc[0]),
                    'Max': ind['max'],
                    'Achievement (%)': (float(w_row[ind['col']].iloc[0]) / ind['max'] * 100) if ind['max'] > 0 else 0
                })
        
        line_df = pd.DataFrame(plot_data)
        
        line = px.line(
            line_df, x='Indicator', y='Achievement (%)',
            markers=True,
            title=f'<b>Detailed Indicator Achievement: {selected_woreda}</b>',
            labels={'Achievement (%)': 'Achievement Rate (%)', 'Indicator': 'Data Element'},
            hover_data={'Max': True, 'Score': True},
            text='Achievement (%)' # Adding value labels
        )
        line.update_layout(
            height=580, 
            paper_bgcolor='white', 
            plot_bgcolor='#f8fafc',
            margin=dict(l=10, r=10, t=80, b=140)
        )
        # Make lines bold and position labels
        line.update_traces(
            line=dict(width=5, color='#1f77b4'), 
            marker=dict(size=12, color='#0a1628'),
            texttemplate='%{text:.1f}%', 
            textposition='top center',
            textfont=dict(size=11, color='#0a1628', family='Inter Bold')
        )
        line.update_xaxes(tickangle=45, showgrid=True, gridwidth=1, gridcolor='#edf2f7')
        line.update_yaxes(range=[0, 115], showgrid=True, gridwidth=1, gridcolor='#edf2f7')
        st.plotly_chart(line, use_container_width=True)


def render_departmental_summary(df: pd.DataFrame):
    """Shows total scores for each Department (Category) per Health Center."""
    categories = sorted(list(set(i['cat'] for i in INDICATORS)))
    
    st.markdown("""
    <style>
    .depttable {
        width: 100%; border-collapse: collapse; border: 4px solid #000000;
        margin: 20px 0; font-family: 'Inter', sans-serif;
    }
    .depttable th {
        background: #1a3a5c; color: white; padding: 14px 10px;
        font-weight: 900; font-size: 0.8rem; border: 2px solid #ffffff;
        text-align: center;
    }
    .depttable td {
        padding: 12px 10px; border: 2px solid #000000;
        font-weight: 800; font-size: 0.9rem; color: #000000;
        text-align: center;
    }
    .depttable tr:nth-child(even) { background: #f8fafc; }
    </style>""", unsafe_allow_html=True)

    header = ['HEALTH CENTER'] + [c.upper() for c in categories] + ['TOTAL', '%']
    html = '<table class="depttable"><thead><tr>'
    for h in header: html += f'<th>{h}</th>'
    html += '</tr></thead><tbody>'

    # Recalculate to be safe
    df = recalculate(df)
    
    for _, row in df.sort_values('percentage', ascending=False).iterrows():
        html += '<tr>'
        html += f'<td style="text-align:left; background:#e2e8f0; font-weight:900;">{row["woreda_name"]}</td>'
        
        for cat in categories:
            cat_cols = [i['col'] for i in INDICATORS if i['cat'] == cat]
            cat_score = sum(row[c] for c in cat_cols if c in df.columns)
            html += f'<td>{cat_score:.1f}</td>'
            
        html += f'<td style="background:rgba(31,119,180,0.1); color:#1f77b4; font-weight:900;">{row["total_score"]:.1f}</td>'
        html += f'<td style="background:rgba(31,119,180,0.1); font-weight:900; text-decoration:underline;">{row["percentage"]:.1f}%</td>'
        html += '</tr>'
        
    html += '</tbody></table>'
    st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# FULL DATA TABLE  (view-only)
# ─────────────────────────────────────────────────────────────────────────────
def render_full_table_readonly(df: pd.DataFrame):
    """Full Performance Report with two-level headers (Departmental Grouping)."""
    # Group indicators by category
    from collections import OrderedDict
    cat_map = OrderedDict()
    for ind in INDICATORS:
        cat = ind['cat']
        if cat not in cat_map: cat_map[cat] = []
        cat_map[cat].append(ind)
    
    st.markdown("""
    <style>
    .fulltable {
        width: 100%; border-collapse: collapse; border: 4px solid #000000;
        margin: 20px 0; font-family: 'Inter', sans-serif;
    }
    .fulltable thead th {
        background: #0a1628; color: white; padding: 10px 5px;
        font-weight: 900; font-size: 0.7rem; border: 2px solid #ffffff;
        text-align: center; text-transform: uppercase;
    }
    .fulltable .cat-header {
        background: #1f77b4; font-size: 0.85rem; letter-spacing: 1px;
    }
    .fulltable td {
        padding: 8px 5px; border: 2px solid #000000;
        font-weight: 800; font-size: 0.8rem; color: #000000;
        text-align: center;
    }
    .fulltable tr:nth-child(even) { background: #f1f5f9; }
    .fulltable .woreda-cell { background: #e2e8f0; text-align: left; font-weight: 900; }
    .fulltable .score-cell { background: rgba(31,119,180,0.05); }
    </style>""", unsafe_allow_html=True)

    # Table Header
    html = '<table class="fulltable"><thead>'
    # Row 1: Categories
    html += '<tr><th rowspan="2">HEALTH CENTER</th>'
    for cat, inds in cat_map.items():
        html += f'<th colspan="{len(inds)}" class="cat-header">{cat}</th>'
    html += '<th rowspan="2">TOTAL</th><th rowspan="2">%</th></tr>'
    
    # Row 2: Indicators
    html += '<tr>'
    for cat, inds in cat_map.items():
        for ind in inds:
            label = ind['label'].replace(' ', '<br>')
            html += f'<th>{label}</th>'
    html += '</tr></thead><tbody>'

    # Rows
    for _, row in df.sort_values('percentage', ascending=False).iterrows():
        html += '<tr>'
        html += f'<td class="woreda-cell">{row["woreda_name"]}</td>'
        for cat, inds in cat_map.items():
            for ind in inds:
                val = row.get(ind['col'], 0)
                # Handle NaN or None safely
                try:
                    fval = float(val)
                    if pd.isna(fval): fval = 0.0
                except:
                    fval = 0.0
                html += f'<td>{fval:.1f}</td>'
        
        total = float(row.get('total_score', 0))
        pct = float(row.get('percentage', 0))
        html += f'<td class="score-cell" style="color:#1f77b4;">{total:.1f}</td>'
        html += f'<td class="score-cell" style="text-decoration: underline;">{pct:.1f}%</td>'
        html += '</tr>'

    html += '</tbody></table>'
    st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# EDIT DATA  (Super Admin only)
# ─────────────────────────────────────────────────────────────────────────────
def render_edit_view():
    page_header("✏️ Edit Performance Data", "Super Admin — Full Edit Access")
    sel_year = st.session_state.get('filter_year', "-- Select Year --")
    sel_q    = st.session_state.get('filter_quarter', "-- Select Quarter --")
    
    if sel_year.startswith("--") or sel_q.startswith("--"):
        st.info("ℹ️ Please select **Year** and **Quarter** from the Global Filters in the sidebar to edit performance data.")
        return
        
    df = load_data()
    if df.empty and 'woreda_name' not in df.columns:
        st.error("❌ Database connection error (KeyError). Performance data could not be loaded.")
        return
    
    st.markdown(f"#### 📅 Period: {sel_year} {sel_q}")

    dept_labels = [i['label'] for i in INDICATORS]
    chosen_label = st.selectbox("📋 Select Department to Edit:", dept_labels, key="sa_sel")
    ind_info = next(i for i in INDICATORS if i['label'] == chosen_label)
    col_key  = ind_info['col']
    col_max  = ind_info['max']

    # ── BLINKING NOTICE ───────────────────────────────────────────────────────
    st.markdown("""
    <div class="entry-notice">
        <span class="entry-notice-icon">⚠️</span>
        <span class="entry-notice-text">YOU SHOULD ENTER DATA FROM 100%</span>
    </div>
    """, unsafe_allow_html=True)

    with st.form(f"sa_form_{col_key}"):
        inputs = {}
        for i, woreda in enumerate(WOREDAS):
            mask = (df['woreda_name'] == woreda) & (df['year'] == sel_year) & (df['quarter'] == sel_q)
            row = df[mask]
            # Convert stored weighted value back to percentage for display
            stored_val = float(row[col_key].iloc[0]) if not row.empty else 0.0
            cur_pct = (stored_val * 100.0 / float(col_max)) if col_max > 0 else 0.0
            bg  = '#f8fafc' if i % 2 == 0 else '#ffffff'
            c1, c2 = st.columns([3, 2])
            with c1:
                st.markdown(f"""
                <div style="background:{bg};padding:9px 16px;border-bottom:1px solid #e2e8f0;
                            border-left:3px solid #ffc107;min-height:52px;display:flex;align-items:center;">
                    <span style="color:#a0aec0;font-size:0.74rem;font-weight:600;margin-right:10px;">#{i+1:02d}</span>
                    <span style="color:#2d3748;font-weight:600;">{woreda}</span>
                </div>""", unsafe_allow_html=True)
            with c2:
                raw_val = st.number_input(
                    f"sa_{i}", min_value=0.0, max_value=None,
                    value=min(cur_pct, 100.0), step=1.0,
                    key=f"sa_{col_key}_{i}", label_visibility="collapsed")
                inputs[woreda] = raw_val
                if raw_val > 100.0:
                    st.markdown('<p style="color:#e53e3e;font-size:0.78rem;margin:2px 0;">⚠️ Max 100%</p>', unsafe_allow_html=True)

        any_invalid = any(v > 100.0 for v in inputs.values())
        _, btn_col, _ = st.columns([1, 2, 1])
        with btn_col:
            saved = st.form_submit_button(f"💾  Save {chosen_label}", use_container_width=True, type="primary")

    if saved:
        if any_invalid:
            st.error("⚠️ Cannot save — some values exceed 100%. Please correct them.")
        else:
            ts = datetime.now().strftime('%Y-%m-%d %H:%M')
            for woreda, val in inputs.items():
                weighted_val = float((val * float(col_max)) / 100.0)
                mask = (df['woreda_name'] == woreda) & (df['year'] == sel_year) & (df['quarter'] == sel_q)
                if mask.any():
                    for idx in df.index[mask]:
                        df.at[idx, col_key]        = weighted_val
                        df.at[idx, 'last_updated'] = ts
            save_data(df, year=sel_year, quarter=sel_q)
            st.session_state.success_msg = f"✅ {chosen_label} data updated successfully!"
            st.rerun()

    footer()


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD  (Admin + Super Admin)
# ─────────────────────────────────────────────────────────────────────────────
def dashboard_view():
    role = st.session_state.role
    page_header("📈 Performance Dashboard",
                f"{'View-only' if role == 'Admin' else 'Super Admin'} — Healthcare Rankings")
    df = load_data()
    if df.empty and 'woreda_name' not in df.columns:
        st.error("❌ Database connection error (KeyError). Dashboard could not be loaded.")
        return
    sel_year = st.session_state.get('filter_year', "-- Select Year --")
    sel_q    = st.session_state.get('filter_quarter', "-- Select Quarter --")
    
    if sel_year.startswith("--") or sel_q.startswith("--"):
        st.info("ℹ️ Please select **Year** and **Quarter** from the Global Filters in the sidebar to view the dashboard.")
        return
    
    # Filter by period
    df = df[(df['year'] == sel_year) & (df['quarter'] == sel_q)].copy()
    if df.empty:
        st.warning(f"No data found for {sel_year} {sel_q}. Showing zeros.")
        rows = []
        for w in WOREDAS:
             rows.append({'woreda_name': w, 'year': sel_year, 'quarter': sel_q, 'total_score':0, 'percentage':0})
        df = pd.DataFrame(rows)
        for i in INDICATORS: df[i['col']] = 0.0

    df = recalculate(df)

    # Sort primarily by performance, and alphabetically as a fallback
    ranked = df.sort_values(['avg_indicator_perf', 'woreda_name'], ascending=[False, True]).reset_index(drop=True)
    
    # Calculate ranks properly (Min rank means ties get the same number, e.g., 1, 1, 1, 4)
    ranked['rank'] = ranked['avg_indicator_perf'].rank(method='min', ascending=False).astype(int)

    # KPI row
    avg_pct   = ranked['avg_indicator_perf'].mean()
    top_row   = ranked.iloc[0]
    bot_row   = ranked.iloc[-1]
    filled    = int((df[[i['col'] for i in INDICATORS]] > 0).any(axis=1).sum())

    k1, k2, k3, k4 = st.columns(4)
    kpi_style = ("background:white;border-radius:12px;padding:18px 14px;"
                 "box-shadow:0 2px 12px rgba(0,0,0,0.07);text-align:center;")

    with k1:
        st.markdown(f"""<div style="{kpi_style}border-top:4px solid #1f77b4;">
            <p style="color:#718096;font-size:0.78rem;font-weight:600;text-transform:uppercase;margin:0;">Woreda Average</p>
            <h2 style="color:#1f77b4;font-size:2rem;margin:8px 0 0;font-weight:800;">{avg_pct:.1f}%</h2></div>""",
            unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div style="{kpi_style}border-top:4px solid #28a745;">
            <p style="color:#718096;font-size:0.78rem;font-weight:600;text-transform:uppercase;margin:0;">Top Health Center 🥇</p>
            <h3 style="color:#28a745;font-size:1rem;margin:8px 0 0;font-weight:800;">{top_row['woreda_name']}</h3>
            <p style="color:#28a745;margin:4px 0 0;font-weight:700;">{top_row['avg_indicator_perf']:.1f}%</p></div>""",
            unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div style="{kpi_style}border-top:4px solid #dc3545;">
            <p style="color:#718096;font-size:0.78rem;font-weight:600;text-transform:uppercase;margin:0;">Lowest Health Center</p>
            <h3 style="color:#dc3545;font-size:1rem;margin:8px 0 0;font-weight:800;">{bot_row['woreda_name']}</h3>
            <p style="color:#dc3545;margin:4px 0 0;font-weight:700;">{bot_row['avg_indicator_perf']:.1f}%</p></div>""",
            unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div style="{kpi_style}border-top:4px solid #7c3aed;">
            <p style="color:#718096;font-size:0.78rem;font-weight:600;text-transform:uppercase;margin:0;">Health Centers with Data</p>
            <h2 style="color:#7c3aed;font-size:2rem;margin:8px 0 0;font-weight:800;">{filled}/{len(WOREDAS)}</h2></div>""",
            unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🏆 Rankings", "📊 Charts", "📋 Full Data"])
    with tab1:
        render_ranking_table(ranked)
    with tab2:
        render_charts(ranked, df)
    with tab3:
        render_full_table_readonly(df)

    footer()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    init_data_file()

    # Auto-login from query parameters to persist authentication on refresh
    if not st.session_state.get('authenticated', False):
        u_param = st.query_params.get("u")
        t_param = st.query_params.get("t")
        if u_param and t_param:
            import hashlib
            user = USERS.get(u_param.strip().lower())
            if user:
                expected_token = hashlib.sha256(f"{u_param.strip().lower()}:{user['ph']}".encode()).hexdigest()
                if t_param == expected_token:
                    st.session_state.authenticated = True
                    st.session_state.username  = u_param.strip().lower()
                    st.session_state.role      = user['role']
                    st.session_state.u_cols    = user.get('cols', [])
                    st.session_state.u_dept    = user.get('dept_name', '')
                    st.session_state.view      = 'Data Entry' if user['role'] == 'Dept Head' else 'Dashboard'
                    if 'filter_year' not in st.session_state:
                         st.session_state.filter_year = "-- Select Year --"
                    if 'filter_quarter' not in st.session_state:
                         st.session_state.filter_quarter = "-- Select Quarter --"

    if not st.session_state.get('authenticated', False):
        login_page()
        return

    render_sidebar()

    # Persistent Toast/Success notification handler
    if st.session_state.get('success_msg'):
        st.success(st.session_state.success_msg)
        if st.session_state.get('show_balloons'):
            st.balloons()
            del st.session_state['show_balloons']
        del st.session_state['success_msg']

    role = st.session_state.role
    view = st.session_state.get('view', 'Dashboard')

    if role == 'Dept Head':
        dept_head_view()

    elif role == 'Admin':
        dashboard_view()

    elif role == 'Super Admin':
        if view == 'Edit Data':
            render_edit_view()
        else:
            dashboard_view()


if __name__ == "__main__":
    main()

# USER CREDENTIALS AND DEPARTMENT MAPPING FIX
# This file contains the complete solution for department head form access issues

# Complete User Credentials Dictionary
USER_CREDENTIALS = {
    "admin": {"password": "admin@2018", "role": "Admin", "dept": "All"},
    "superadmin": {"password": "super@2024", "role": "Super Admin", "dept": "All"},
    "epi": {"password": "EPI@2024", "role": "Department Head", "dept": "EPI"},
    "tb": {"password": "TB@2024", "role": "Department Head", "dept": "TB & Leprosy"},
    "child health": {"password": "Child Health@2024", "role": "Department Head", "dept": "Child Health"},
    "phem": {"password": "PHEM@2024", "role": "Department Head", "dept": "PHEM"},
    "cbhi": {"password": "CBHI@2024", "role": "Department Head", "dept": "CBHI"},
    "finance": {"password": "Finance@2024", "role": "Department Head", "dept": "Finance"},
    "plan": {"password": "Plan@2024", "role": "Department Head", "dept": "Plan"},
    "wt": {"password": "WT@2024", "role": "Department Head", "dept": "WT"},
    "medical": {"password": "Medical@2024", "role": "Department Head", "dept": "Medical Service"},
    "rmh": {"password": "RMH@2024", "role": "Department Head", "dept": "RMH"},
    "pharmacy": {"password": "Pharmacy@2024", "role": "Department Head", "dept": "Pharmacy & Logistic"},
    "ultrasound": {"password": "Ultrasound@2024", "role": "Department Head", "dept": "Ultrasound"},
    "apts": {"password": "APTS@2024", "role": "Department Head", "dept": "APTS"},
    "community_pharmacy": {"password": "CommunityPharmacy@2024", "role": "Department Head", "dept": "Community Pharmacy"},
    "dm_test": {"password": "DMTest@2024", "role": "Department Head", "dept": "DM Test"},
    "full_emr": {"password": "FullEMR@2024", "role": "Department Head", "dept": "Full EMR"},
    "epi_modernization": {"password": "EPIModernization@2024", "role": "Department Head", "dept": "EPI Modernization"},
    "zero_dose": {"password": "ZeroDose@2024", "role": "Department Head", "dept": "Zero Dose"},
    "multi_sectoral": {"password": "MultiSectoral@2024", "role": "Department Head", "dept": "Multi-Sectoral"},
    "cash_program": {"password": "CashProgram@2024", "role": "Department Head", "dept": "Cash Program"},
    "hygiene": {"password": "Hygiene@2024", "role": "Department Head", "dept": "Hygiene & Sanitation"},
    "hiv_sti": {"password": "HIVSTI@2024", "role": "Department Head", "dept": "HIV/STI"}
}

# Department to Column Mapping
DEPARTMENT_COLUMN_MAPPING = {
    'EPI': 'epi',
    'TB & Leprosy': 'tb_leprosy', 
    'Child Health': 'child_health',
    'PHEM': 'phem',
    'CBHI': 'cbhi',
    'Finance': 'finance',
    'Plan': 'plan',
    'WT': 'wt',
    'Medical Service': 'medical_service',
    'RMH': 'rmh',
    'Pharmacy & Logistic': 'pharmacy_logistic',
    'Ultrasound': 'ultrasound',
    'APTS': 'apts',
    'Community Pharmacy': 'community_pharmacy',
    'DM Test': 'dm_test',
    'Full EMR': 'full_emr',
    'EPI Modernization': 'epi_modernization',
    'Zero Dose': 'zero_dose',
    'Multi-Sectoral': 'multi_sectoral',
    'Cash Program': 'cash_program',
    'Hygiene & Sanitation': 'hygiene_sanitation',
    'HIV/STI': 'hiv_sti'
}

# Department Configuration with Exact Column Names
DEPARTMENT_CONFIG = {
    'EPI': {
        'column': 'epi',
        'label': 'EPI',
        'max': 5,
        'category': 'Prevention & Disease'
    },
    'TB & Leprosy': {
        'column': 'tb_leprosy',
        'label': 'TB & Leprosy',
        'max': 5,
        'category': 'Prevention & Disease'
    },
    'Child Health': {
        'column': 'child_health',
        'label': 'Child Health',
        'max': 5,
        'category': 'Prevention & Disease'
    },
    'PHEM': {
        'column': 'phem',
        'label': 'PHEM',
        'max': 5,
        'category': 'Prevention & Disease'
    },
    'CBHI': {
        'column': 'cbhi',
        'label': 'CBHI',
        'max': 10,
        'category': 'Admin & Finance'
    },
    'Finance': {
        'column': 'finance',
        'label': 'Finance',
        'max': 5,
        'category': 'Admin & Finance'
    },
    'Plan': {
        'column': 'plan',
        'label': 'Plan',
        'max': 5,
        'category': 'Admin & Finance'
    },
    'WT': {
        'column': 'wt',
        'label': 'WT',
        'max': 5,
        'category': 'Admin & Finance'
    },
    'Medical Service': {
        'column': 'medical_service',
        'label': 'Medical Service',
        'max': 15,
        'category': 'Medical & Pharmacy'
    },
    'RMH': {
        'column': 'rmh',
        'label': 'RMH',
        'max': 10,
        'category': 'Medical & Pharmacy'
    },
    'Pharmacy & Logistic': {
        'column': 'pharmacy_logistic',
        'label': 'Pharmacy & Logistic',
        'max': 5,
        'category': 'Medical & Pharmacy'
    },
    'Ultrasound': {
        'column': 'ultrasound',
        'label': 'Ultrasound',
        'max': 2.5,
        'category': 'Medical & Pharmacy'
    },
    'APTS': {
        'column': 'apts',
        'label': 'APTS',
        'max': 2.5,
        'category': 'Medical & Pharmacy'
    },
    'Community Pharmacy': {
        'column': 'community_pharmacy',
        'label': 'Community Pharmacy',
        'max': 2.5,
        'category': 'Medical & Pharmacy'
    },
    'DM Test': {
        'column': 'dm_test',
        'label': 'DM Test',
        'max': 2.5,
        'category': 'Medical & Pharmacy'
    },
    'Full EMR': {
        'column': 'full_emr',
        'label': 'Full EMR',
        'max': 5,
        'category': 'Innovation & Quality'
    },
    'EPI Modernization': {
        'column': 'epi_modernization',
        'label': 'EPI Modernization',
        'max': 2.5,
        'category': 'Innovation & Quality'
    },
    'Zero Dose': {
        'column': 'zero_dose',
        'label': 'Zero Dose',
        'max': 2.5,
        'category': 'Innovation & Quality'
    },
    'Multi-Sectoral': {
        'column': 'multi_sectoral',
        'label': 'Multi-Sectoral',
        'max': 2.5,
        'category': 'Innovation & Quality'
    },
    'Cash Program': {
        'column': 'cash_program',
        'label': 'Cash Program',
        'max': 2.5,
        'category': 'Innovation & Quality'
    },
    'Hygiene & Sanitation': {
        'column': 'hygiene_sanitation',
        'label': 'Hygiene & Sanitation',
        'max': 5,
        'category': 'Innovation & Quality'
    },
    'HIV/STI': {
        'column': 'hiv_sti',
        'label': 'HIV/STI',
        'max': 5,
        'category': 'Innovation & Quality'
    }
}

# Function to get department config
def get_department_config(department_name):
    """Get department configuration by name"""
    return DEPARTMENT_CONFIG.get(department_name)

# Function to get user credentials
def get_user_credentials(username):
    """Get user credentials by username"""
    return USER_CREDENTIALS.get(username)

# Function to verify department access
def verify_department_access(username, department):
    """Verify if user has access to department"""
    user_creds = get_user_credentials(username)
    if not user_creds:
        return False
    
    if user_creds['role'] == 'Admin' or user_creds['role'] == 'Super Admin':
        return True
    
    return user_creds.get('dept') == department

# Function to get department column name
def get_department_column(department_name):
    """Get database column name for department"""
    return DEPARTMENT_COLUMN_MAPPING.get(department_name)

# Debug function to check all mappings
def debug_department_mappings():
    """Debug function to check all department mappings"""
    print("=== DEPARTMENT MAPPINGS DEBUG ===")
    print("User Credentials:")
    for username, creds in USER_CREDENTIALS.items():
        if creds['role'] == 'Department Head':
            print(f"  {username} -> {creds['dept']}")
    
    print("\nDepartment Column Mapping:")
    for dept, column in DEPARTMENT_COLUMN_MAPPING.items():
        print(f"  {dept} -> {column}")
    
    print("\nDepartment Config:")
    for dept, config in DEPARTMENT_CONFIG.items():
        print(f"  {dept} -> {config['column']} (max: {config['max']})")

if __name__ == "__main__":
    debug_department_mappings()

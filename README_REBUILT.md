# Healthcare Performance System - Rebuilt

## What's New

This rebuilt version features:

✅ **CSV-based storage** - All data stored in `performance_data.csv`
✅ **Clean HTML tables** - Rankings displayed as styled HTML tables (no code visible)
✅ **Hidden Streamlit branding** - Menu, footer, and header removed
✅ **Role-based access control** - Department heads see only their department
✅ **Auto-calculated scores** - Total scores and percentages calculated automatically
✅ **Clean UI** - Simplified, professional interface

## Quick Start

```bash
pip install streamlit pandas plotly
streamlit run app_rebuilt.py
```

## Login Credentials

### Department Heads (Data Entry Only)
- **EPI**: `epi` / `EPI@2024`
- **Child Health**: `child_health` / `ChildHealth@2024`
- **TB & Leprosy**: `tb` / `TB@2024`
- **PHEM**: `phem` / `PHEM@2024`
- **CBHI**: `cbhi` / `CBHI@2024`
- **Finance**: `finance` / `Finance@2024`
- **Plan**: `plan` / `Plan@2024`
- **WT**: `wt` / `WT@2024`
- **Medical Service**: `medical` / `Medical@2024`
- **RMH**: `rmh` / `RMH@2024`
- **Pharmacy & Logistic**: `pharmacy` / `Pharmacy@2024`

### Admin (View Only)
- **Username**: `admin`
- **Password**: `admin@2018`

### Super Admin (Full Access)
- **Username**: `superadmin`
- **Password**: `super@2024`

## Features by Role

### Department Heads
- Select woreda from dropdown
- Enter scores for their department's indicators
- View calculated totals and percentages
- Save data to CSV

### Adm
# Healthcare Performance Management System

A comprehensive web application for monitoring and ranking healthcare performance across 23 Woredas with role-based access control.

## Features

### Role-Based Access Control
- **Department Heads**: Can only enter data for their specific department
- **Admin**: Read-only access to all rankings and visualizations
- **Super Admin**: Full CRUD operations on all data

### Performance Indicators (Total: 105 points)

#### Medical & Pharmacy (37.5 pts)
- Medical service (15 pts)
- RMH (10 pts)
- Pharmacy & logistic (5 pts)
- Ultrasound (2.5 pts)
- APTS (2.5 pts)
- Community pharmacy (2.5 pts)
- DM test (2.5 pts)

#### Prevention & Disease (20 pts)
- EPI (5 pts)
- Child health (5 pts)
- TB & Leprosy (5 pts)
- PHEM (5 pts)

#### Admin & Finance (25 pts)
- CBHI (10 pts)
- Finance (5 pts)
- Plan (5 pts)
- WT (5 pts)

#### Innovation & Quality (22.5 pts)
- Full EMR (5 pts)
- EPI modernization (5 pts)
- Zero dose (5 pts)
- Multi-Sectoral (2.5 pts)
- Cash program (5 pts)
- Hygiene & Sanitation (5 pts)
- HIV/STI (5 pts)

## Installation

1. Clone or download the project files
2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
streamlit run app.py
```

2. Open your browser and navigate to `http://localhost:8501`

## Deployment

### Option 1: Streamlit Cloud (Recommended)
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select your repository and main file (`app.py`)
5. Click "Deploy"

### Option 2: Railway
1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Initialize: `railway init`
4. Deploy: `railway up`

### Option 3: Heroku
1. Create `Procfile`:
```
web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```
2. Deploy to Heroku using CLI or GitHub integration

### Option 4: VPS/Cloud Server
1. Install dependencies on server
2. Use systemd or PM2 for process management
3. Configure nginx as reverse proxy (optional)
4. Set up SSL certificate

## Default Login Credentials

### Department Heads
- **EPI**: Username: `epi`, Password: `EPI@2024`
- **TB**: Username: `tb`, Password: `TB@2024`
- **Child Health**: Username: `child health`, Password: `Child Health@2024`
- **PHEM**: Username: `phem`, Password: `PHEM@2024`
- **CBHI**: Username: `cbhi`, Password: `CBHI@2024`
- **Finance**: Username: `finance`, Password: `Finance@2024`
- **Plan**: Username: `plan`, Password: `Plan@2024`
- **WT**: Username: `wt`, Password: `WT@2024`

### Admin
- **Username**: `admin`
- **Password**: `admin@2018`

### Super Admin
- **Username**: `superadmin`
- **Password**: `super@2024`

## Dashboard Features

### Department Head Interface
- Select Woreda from dropdown
- Enter scores for department-specific indicators
- Save data automatically

### Admin Dashboard
- KPI cards showing average score, top and least performing Woredas
- Interactive bar chart showing all Woreda rankings
- Radar chart for detailed performance analysis
- Detailed data tables

### Super Admin Dashboard
- All Admin features plus:
- Edit mode for modifying any data entry
- Delete functionality for records
- Full data management capabilities

## Database Structure

The application uses SQLite with two main tables:
- `users`: Stores user credentials and roles
- `performance_data`: Stores all performance indicators and calculated scores

## Technical Stack

- **Backend**: Python
- **Frontend**: Streamlit
- **Database**: SQLite
- **Visualization**: Plotly
- **Data Processing**: Pandas

## File Structure

```
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── README.md             # This documentation
└── healthcare_performance.db  # SQLite database (created automatically)
```

## Notes

- The database is created automatically when you first run the application
- All data is stored locally in the SQLite database
- The application calculates total scores and percentages automatically
- Rankings are updated in real-time as data is entered

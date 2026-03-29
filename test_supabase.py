import requests
import json

SUPABASE_URL = "https://xjbntmsacknqmymvxoig.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhqYm50bXNhY2tucW15bXZ4b2lnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI0NDY4MjIsImV4cCI6MjA4ODAyMjgyMn0.2WfPhlZZ3RMtJqfNBIQcQfMwAnjA9Yp-dtnzfFgw-XI"

def check_connection():
    print(f"📡 Testing connection to {SUPABASE_URL}...")
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    
    # Try to fetch performance_data table
    try:
        response = requests.get(f"{SUPABASE_URL}/rest/v1/performance_data?limit=1", headers=headers)
        if response.status_code == 200:
            print("✅ Connection Successful! 'performance_data' table is reachable.")
            print(f"Data Sample: {response.json()}")
        elif response.status_code == 404:
            print("⚠️ Connection Successful, but 'performance_data' table NOT found.")
            print("Please create the table manually in Supabase with these columns:")
            print("woreda_name (text), year (text), quarter (text) and all indicators (float).")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    check_connection()

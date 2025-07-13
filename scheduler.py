import time
import mysql.connector
import subprocess
from datetime import datetime

def get_latest_record_count():
    try:
        conn = mysql.connector.connect(
            host='mysql',
            user='hlruser',
            password='hlrpass',
            database='HLRDB'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM hlr_verification")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except:
        return 0

def run_data_sync():
    print(f"New records detected at {datetime.now()}")
    subprocess.run(['python', 'data_sync.py'])

def monitor_and_sync():
    last_count = get_latest_record_count()
    print(f"Starting monitor. Current records: {last_count}")
    
    while True:
        time.sleep(300)  # Check every 5 minutes
        current_count = get_latest_record_count()
        
        if current_count > last_count:
            print(f"Records increased: {last_count} -> {current_count}")
            run_data_sync()
            last_count = current_count
        else:
            print(f"No new records. Count: {current_count}")

if __name__ == "__main__":
    monitor_and_sync()
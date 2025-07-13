import json
import mysql.connector
import pandas as pd
import subprocess
from datetime import datetime

def fetch_and_push_data():
    # Get data from local MySQL instead of server
    conn = mysql.connector.connect(
        host='mysql',
        user='hlruser',
        password='hlrpass',
        database='HLRDB'
    )
    
    df = pd.read_sql("SELECT operation, bss_msisdn, hlr_msisdn, file_name FROM hlr_verification ORDER BY record_timestamp DESC LIMIT 100", conn)
    conn.close()
    
    all_data = df.to_dict('records')
    

    
    # Save to JSON file
    with open('hlr_data.json', 'w') as f:
        json.dump(all_data, f)
    
    # Git push
    subprocess.run(['git', 'add', 'hlr_data.json'])
    subprocess.run(['git', 'commit', '-m', f'Update HLR data {datetime.now()}'])
    subprocess.run(['git', 'push'])

if __name__ == "__main__":
    fetch_and_push_data()
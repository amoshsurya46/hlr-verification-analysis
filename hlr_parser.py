import json
import mysql.connector
import paramiko
import os
from datetime import datetime

def connect_to_server():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('10.63.11.11', username='jboss', password='jboss')
    return ssh

def get_hlr_files(ssh):
    sftp = ssh.open_sftp()
    remote_path = '/apps/jboss-5.1.0.GA/server/HKsmfagent/HLRVERIFYJOBPDF/'
    files = sftp.listdir(remote_path)
    
    hlr_files = [f for f in files if f.startswith('hlrout_')]
    
    for file in hlr_files:
        sftp.get(f"{remote_path}{file}", f"./data/{file}")
    
    sftp.close()
    return hlr_files

def parse_and_insert_data():
    conn = mysql.connector.connect(
        host='mysql',
        user='hlruser',
        password='hlrpass',
        database='HLRDB'
    )
    cursor = conn.cursor()
    
    os.makedirs('./data', exist_ok=True)
    
    ssh = connect_to_server()
    files = get_hlr_files(ssh)
    ssh.close()
    
    for file in files:
        with open(f'./data/{file}', 'r') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line.strip())
                    
                    bss_data = data['BSS'][0] if data['BSS'] else {}
                    hlr_data = data['HLR'][0] if data['HLR'] else {}
                    
                    cursor.execute("""
                        INSERT INTO hlr_verification 
                        (operation, bss_msisdn, bss_imsi, hlr_msisdn, hlr_imsi, file_name)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        data['operation'],
                        bss_data.get('msisdn_no', ''),
                        bss_data.get('imsi_no', ''),
                        hlr_data.get('msisdn_no', ''),
                        hlr_data.get('imsi_no', ''),
                        file
                    ))
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    parse_and_insert_data()
    print("Data imported successfully!")
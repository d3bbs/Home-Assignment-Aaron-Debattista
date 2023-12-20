import time
import sqlite3
from paramiko import SSHClient
from github import Github

# backup)time is the time at which the backup should be taken
def get_backup_time():
    conn = sqlite3.connect('router_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT backup_time FROM backup")
    backup_time = cursor.fetchone()
    return backup_time
\
# list_routers() returns a list of all the routers in the database
def list_routers():
    conn = sqlite3.connect('router_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM routers")
    devices = cursor.fetchall()
    return [{'router_name': device[1], 'ip_address': device[2], 'username': device[3], 'password': device[4]} for device in devices]
\
# backup_router(router) backs up the configuration of the router
def backup_router(router):
    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(router['ip_address'], username=router['username'], password=router['password'])
    stdin, stdout, stderr = ssh.exec_command('show running-config')
    config = stdout.read()
    with open(f"{router['ip_address']}.config", 'w') as f:
        f.write(config)
    ssh.close()

# upload_to_github(filename) uploads the file to github
def upload_to_github(filename):
    g = Github("<github_token>")
    repo = g.get_user().get_repo("<repo_name>")
    with open(filename, 'r') as f:
        content = f.read()
    repo.create_file(filename, "backup", content)
# run_service() runs the service
def run_service():
    while True:
        current_time = time.strftime("%H:%M")
        backup_time = get_backup_time()
        if current_time == backup_time:
            routers = list_routers()
            for router in routers:
                backup_router(router)
                upload_to_github(f"{router['ip_address']}.config")
        time.sleep(60)

run_service()
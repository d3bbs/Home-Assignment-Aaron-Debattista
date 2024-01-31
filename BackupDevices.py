import time
import sqlite3
import paramiko
from github import Github
import socket
def handle_request(sock):
    request = sock.recv(1024).decode('utf-8')
    action, data = request.split(':', 1)
    if action == "BACKUP":
        set_backup_time(data)
        sock.sendall(b"Backup time set successfully.")
    else:
        sock.sendall(b"Invalid request.")

# set_backup_time(backup_time) sets the backup time
def set_backup_time(backup_time):
    print(f"Setting backup time to {backup_time}")
    conn = sqlite3.connect('router_database.db')
    cursor = conn.cursor()
    print("Checking database...")
    #if the length of the list returned by the query is 5, then the time column does not exist
    if len(list(cursor.execute("PRAGMA table_info(routers)"))) == 5:
        cursor.execute("ALTER TABLE routers ADD COLUMN time TEXT")
        print("Added time column to routers table.")
    cursor.execute("UPDATE routers SET time=?", (backup_time,))
    conn.commit()
    print("Backup time set successfully.")
    return 
# get_backup_time() returns the backup time
def get_backup_time():
    conn = sqlite3.connect('router_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT time FROM routers")
    result = cursor.fetchone()
    # Check if result is not None (which means the query returned a row)
    if result is not None:
        # Get the first (and only) element of the tuple
        backup_time = result[0]
    else:
        backup_time = None
    return backup_time

# list_routers() returns a list of all the routers in the database
def list_routers():
    conn = sqlite3.connect('router_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM routers")
    devices = cursor.fetchall()
    return [{'router_name': device[1], 'ip_address': device[2], 'username': device[3], 'password': device[4]} for device in devices]

# backup_router(router) backs up the configuration of the router
def backup_router(router):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    ssh.connect(router['ip_address'], username=router['username'], password=router['password'])
    stdin, stdout, stderr = ssh.exec_command('show running-config')
    config = stdout.read()
    with open(f"{router['ip_address']}.config", 'w') as f:
        f.write(config.decode())
    ssh.close()

# upload_to_github(filename) uploads the file to github
def upload_to_github(filename):
    #access token
    g = Github("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")
    #get the repository
    repo = g.get_user().get_repo("Home-Assignment-Aaron-Debattista")
    with open(filename, 'r') as f:
        content = f.read()
    # Check if the file already exists in the repository
    try:
        print(f"Content of {filename}: {content}")
        file = repo.get_contents(filename)
        repo.update_file(file.path, "backup", content, file.sha)
    # If the file does not exist, create it
    except Github.UnknownObjectException:
        print(f"Content of {filename}: {content}")
        repo.create_file(filename, "backup", content)
        

# run_service() runs the service
def run_service():
    print("Service running on port 12346.")    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('localhost', 12346))
        s.listen()
        conn, addr = s.accept()
        print(f"Connected to {addr}")
        with conn:
            handle_request(conn)
            while True:
                conn = sqlite3.connect('router_database.db')
                cursor = conn.cursor()
                print("Checking backup time...")
                current_time = time.strftime("%H:%M")
                current_time= str(current_time).strip()
                print("Current time: " + current_time)
                backup_time = get_backup_time()
                backup_time = str(backup_time).strip()
                print("Backup time: " + backup_time)
                if current_time == backup_time:
                    print("Backing up routers...")
                    routers = list_routers()
                    for router in routers:
                        backup_router(router)
                        upload_to_github(f"{router['ip_address']}.config")
                    print("Backup complete.")
                else:
                    print("Backup time not reached yet.")
                    time.sleep(60)

def handle_request(sock):
    request = sock.recv(1024).decode('utf-8')
    print(f"Received request: {request}")
    action, data = request.split(':', 1)
    if action == "BACKUP":
        set_backup_time(data)
        response = "Backup time set successfully."
    else:
        response = "Invalid request."
    sock.sendall(response.encode('utf-8'))
    
if __name__ == "__main__":
    run_service()

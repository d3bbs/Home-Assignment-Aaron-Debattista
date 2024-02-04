import socket
import ssl
from BackupDevices import *
from elasticsearch import Elasticsearch
import sqlite3
import datetime
import difflib
import matplotlib.pyplot as plt

HOST = 'localhost'  # The server's hostname or IP address
managedev = 12345        # The port used by the manage devices server
backupdev = 12346 # The port used by the backup devices server


def dev_send_request(action, data='None'):
    with socket.create_connection((HOST, managedev)) as sock:
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_cert_chain(certfile='client.crt', keyfile='client.key')
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        with context.wrap_socket(sock, server_hostname=HOST) as ssock:
            if data is not None:
                request = f"{action}:{','.join(data)}"
            else:
                request = action
            ssock.sendall(request.encode('utf-8'))

            response = ssock.recv(1024).decode('utf-8')
            print(response)
def backup_send_request(action, data='None'):
    with socket.create_connection((HOST, backupdev)) as sock:
        with sock.makefile('rw') as ssock:
            if data is not None:
                request = f"{action}:{','.join(data)}"
            else:
                request = action
            ssock.write(request + '\n')
            ssock.flush()

            response = ssock.readline().strip()
            print(response)
            
            
def setNetflowSettings(router_ip):
    # Connect to the database
    conn = sqlite3.connect('router_database.db')
    cursor = conn.cursor()
    # Get the username and password for the router
    cursor.execute('SELECT username, password FROM routers WHERE ip_address = ?', (router_ip,))
    result = cursor.fetchone()
    if result is None:
        print(f"No router found with IP address {router_ip}")
        return
    username, password = result
    # Create a new SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # Connect to the router
    client.connect(router_ip, username=username, password=password)
    # Send the commands to set the Netflow settings
    shell= client.invoke_shell()
    commands = [
        "conf t",
        "ip flow-cache timeout inactive 10",
        "ip flow-cache timeout active 10",
        "ip flow-export source FastEthernet0/0",
        "ip flow-export version 9",
        "ip flow-export destination 192.168.122.1 2055",
        "int fa0/0",
        "ip flow ingress",
        "ip flow egress",
        "exit"
    ]
    for command in commands:
        shell.send(command + "\n")
        time.sleep(1)
    output = shell.recv(1000)
    print(output.decode())
    # Close the connection
    client.close()
    # Close the database connection
    conn.close()

def removeNetflowSettings(router_ip):
        # Connect to the database
    conn = sqlite3.connect('router_database.db')
    cursor = conn.cursor()
    # Get the username and password for the router
    cursor.execute('SELECT username, password FROM routers WHERE ip_address = ?', (router_ip,))
    result = cursor.fetchone()
    if result is None:
        print(f"No router found with IP address {router_ip}")
        return
    username, password = result
    # Create a new SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # Connect to the router
    client.connect(router_ip, username=username, password=password)
    shell= client.invoke_shell()
    # Send the commands to set the Netflow settings
    commands = [
        f"conf t",
        f"no ip flow-cache timeout inactive 10",
        f"no ip flow-cache timeout active 10",
        f"no ip flow-export source FastEthernet0/0",
        f"no ip flow-export version 9",
        f"no ip flow-export destination 192.168.122.1 2055",
        f"int fa0/0",
        f"no ip flow ingress",
        f"no ip flow egress"
    ]
    for command in commands:
        shell.send(command + "\n")
        time.sleep(1)
    output = shell.recv(1000)
    print(output.decode())
    # Close the connection
    client.close()
    # Close the database connection
    conn.close()

def setSNMPSettings(router_ip):
        # Connect to the database
    conn = sqlite3.connect('router_database.db')
    cursor = conn.cursor()
    # Get the username and password for the router
    cursor.execute('SELECT username, password FROM routers WHERE ip_address = ?', (router_ip,))
    result = cursor.fetchone()
    if result is None:
        print(f"No router found with IP address {router_ip}")
        return
    username, password = result
    # Create a new SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # Connect to the router
    client.connect(router_ip, username=username, password=password)
    shell= client.invoke_shell()  
    # Send the commands to set the Netflow settings
    commands = [
        f"conf t",
        "logging history debugging",
        "snmp-server community SFN RO",
        "snmp-server ifindex persist",
        "snmp-server enable traps snmp linkdown linkup",
        "snmp-server enable traps syslog",
        "snmp-server host 192.168.122.2 version 2c SFN"
    ]
    for command in commands:
        shell.send(command + "\n")
        time.sleep(1)
    output = shell.recv(1000)
    print(output.decode())
    # Close the connection
    client.close()
    # Close the database connection
    conn.close()
    
def removeSNMPSettings(router_ip):
        # Connect to the database
    conn = sqlite3.connect('router_database.db')
    cursor = conn.cursor()
    # Get the username and password for the router
    cursor.execute('SELECT username, password FROM routers WHERE ip_address = ?', (router_ip,))
    result = cursor.fetchone()
    if result is None:
        print(f"No router found with IP address {router_ip}")
        return
    username, password = result
    # Create a new SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # Connect to the router
    client.connect(router_ip, username=username, password=password)
    shell= client.invoke_shell()
    # Send the commands to set the Netflow settings
    commands = [
        f"conf t",
        "no logging history debugging",
        "no snmp-server community SFN RO",
        "no snmp-server ifindex persist",
        "no snmp-server enable traps snmp linkdown linkup",
        "no snmp-server enable traps syslog",
        "no snmp-server host 192.168.122.2 version 2c SFN"
    ]
    for command in commands:
        shell.send(command + "\n")
        time.sleep(1)
    output = shell.recv(1000)
    print(output.decode())
    # Close the connection
    client.close()
    # Close the database connection
    conn.close()


def display_backup_changes(router_ip):
    # Connect to the database
    conn = sqlite3.connect('router_database.db')
    cursor = conn.cursor()

    # Get all backup dates for the router
    cursor.execute('SELECT time FROM routers WHERE ip_address = ?', (router_ip,))
    backup_dates = cursor.fetchall()

    # Display the dates to the user
    print("Available backup dates:")
    for i, date in enumerate(backup_dates):
        print(f"{i+1}. {date[0]}")

    # Ask the user to select a date
    date_choice = int(input("Select a date: ")) - 1
    selected_date = backup_dates[date_choice][0]

    # Get the backup for the selected date
    with open(f'{router_ip}.config', 'r') as file:
        backup_config = file.read()
    # Get the router's username
    cursor.execute('SELECT username FROM routers WHERE ip_address = ?', (router_ip,))
    router_username = cursor.fetchone()[0]

    # Get the current config from the router
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(router_ip, username=router_username, password='password')
    stdin, stdout, stderr = ssh.exec_command('show running-config')
    current_config = stdout.read().decode('utf-8')

    # Compare the two configs and display the differences
    diff = difflib.unified_diff(backup_config.splitlines(), current_config.splitlines())
    print('\n'.join(diff))

    # Close the SSH and database connections
    ssh.close()
    conn.close()

def display_packets_per_protocol(router_ip):
    # Connect to the database
    conn = sqlite3.connect('netflow_data.db')
    cursor = conn.cursor()

    # Get the number of packets per protocol for the router
    cursor.execute('SELECT protocol, COUNT(*) FROM netflow_data WHERE router_ip = ? GROUP BY protocol', (router_ip,))
    packets_per_protocol = cursor.fetchall()

    # Calculate the total number of packets
    total_packets = sum(count for protocol, count in packets_per_protocol)

    # Calculate the percentages for each protocol
    percentages = [(protocol, count / total_packets * 100) for protocol, count in packets_per_protocol]

    # Create a pie chart
    plt.pie([percentage for protocol, percentage in percentages], labels=[protocol for protocol, percentage in percentages], autopct='%1.1f%%')
    plt.title('Percentage of packets per protocol')
    plt.show()

    # Close the database connection
    conn.close()

# Establish a connection to the Elasticsearch server
def export_syslog_to_elasticsearch(router_ip):
    # Connect to the database
    conn = sqlite3.connect('router_database.db')
    cursor = conn.cursor()

    # Connect to the exceptions database
    exceptions_conn = sqlite3.connect('exceptions.db')
    exceptions_cursor = exceptions_conn.cursor()
    exceptions_cursor.execute('''
        CREATE TABLE IF NOT EXISTS exceptions (
            timestamp TEXT,
            router_ip TEXT,
            exception TEXT
        )
    ''')

        # Connect to Elasticsearch
    es = Elasticsearch(
        cloud_id="WUJGY2FvMEJBWHFiUTNjS1Bwdl86UEI2cjU0YzJUQnFqY3B6TXRPS3JKQQ==",
        http_auth=("elastic", "changeme")
    )

    # Get the syslog entries for the router
    cursor.execute('SELECT * FROM syslog WHERE router_ip = ?', (router_ip,))
    syslog_entries = cursor.fetchall()

    # Export the syslog entries to Elasticsearch
    for entry in syslog_entries:
        doc = {
            'router_ip': entry[0],
            'timestamp': entry[1],
            'message': entry[2]
        }
        es.index(index="syslog", doc_type='entry', body=doc)

    # Query Elasticsearch for link state changes
    body = {
        "query": {
            "bool": {
                "must": [
                    { "match": { "router_ip": router_ip } },
                    { "match": { "message": "link state change" } }
                ]
            }
        }
    }


while True:
    print("~~~Menu~~~")
    print("1. Add Router")
    print("2. Delete Router")
    print("3. List Router")
    print("4. Set Backup Time")
    print("5. Set Router Netflow Settings")
    print("6. Remove Router Netflow Settings")
    print("7. Set Router SNMP Settings")
    print("8. Remove Router SNMP Settings")
    print("9. Show Router Config")
    print("10. Show Changes in Router Config")
    print("11. Display Router Netflow Statistics")
    print("12. Show Router Syslog")
    print("13. Exit")

    choice = input("Enter your choice: ")
    if choice == "1":
        router_name = input("Enter router name:\n")
        username= input("Enter username:\n")
        password = input("Enter password:\n")
        ip_address = input("Enter ip address:\n")
        dev_send_request("ADD", [router_name, ip_address, username, password,])
    elif choice == "2":
        data = input("Enter router name to delete: ")
        dev_send_request("DELETE", [data])
    elif choice == "3":
        response = dev_send_request("LIST", [])
    elif choice == "4":
        backup_time = input("Enter backup time: ")
        backup_send_request("BACKUP", [backup_time])
    elif choice == "5":
        ip_address = input("Enter router ip: ")
        setNetflowSettings(ip_address)
    elif choice == "6":
        ip_address = input("Enter router ip: ")
        removeNetflowSettings(ip_address)
    elif choice == "7":
        ip_address = input("Enter router ip: ")
        setSNMPSettings(ip_address)
    elif choice == "8":
        ip_address = input("Enter router ip: ")
        removeSNMPSettings(ip_address)
    elif choice == "9":
        ip_address = input("Please enter the router IP: ")
        dev_send_request("SHOW_CONFIG", [ip_address])
    elif choice =='10':
        ip_address = input("Please enter the router IP: ")
        display_backup_changes(ip_address)
    elif choice == "11":
        ip_address = input("Please enter the router IP: ")
        display_packets_per_protocol(ip_address)
    elif choice == "12":
        router_ip = input("Enter the router IP address: ")
        export_syslog_to_elasticsearch(router_ip)
    elif choice == "13":
        break
    else:
        print("Invalid choice. Please try again.")
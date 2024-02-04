from scapy.all import *
from scapy.layers.inet import IP, TCP, UDP
from datetime import datetime
import sqlite3
from scapy.all import sniff
import scapy.layers.netflow as NetflowDataFlowSet
import socket
import paramiko

# Create a database connection
conn = sqlite3.connect('netflow_data.db')
cursor = conn.cursor()
#Create a table to store the NetFlow data
cursor.execute('''
    CREATE TABLE IF NOT EXISTS netflow_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        time TEXT,
        router_ip TEXT,
        num_packets INTEGER,
        source_ip TEXT,
        destination_ip TEXT,
        protocol TEXT,
        source_port INTEGER,
        destination_port INTEGER
    )   
''')

# Define a callback function to process the captured NetFlow packets
def process_packet(packet):
    # Get the current date and time
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")
    # Get the router IP address
    router_ip = packet[IP].src
    # Get the number of packets
    num_packets = packet[UDP].len
    # Get the source IP address
    source_ip = packet[IP].src
    # Get the destination IP address
    destination_ip = packet[IP].dst
    # Get the protocol
    protocol = packet[IP].proto
    # Get the source port
    source_port = packet[UDP].sport
    # Get the destination port
    destination_port = packet[UDP].dport
    # Insert the NetFlow data into the database
    cursor.execute('''
        INSERT INTO netflow_data (date, time, router_ip, num_packets, source_ip, destination_ip, protocol, source_port, destination_port)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (current_date, current_time, router_ip, num_packets, source_ip, destination_ip, protocol, source_port, destination_port))
    conn.commit()
    # Close the connection with the client
    
sniff(filter="udp and port 2055", prn=process_packet, store=0)
        






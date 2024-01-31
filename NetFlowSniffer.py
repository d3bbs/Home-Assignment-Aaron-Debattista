from scapy.all import *
from scapy.layers.inet import IP, TCP, UDP
from datetime import datetime
import sqlite3
from scapy.all import sniff
import scapy.layers.netflow as NetflowDataFlowSet


# Create a database connection
conn = sqlite3.connect('netflow_data.db')
cursor = conn.cursor()

# Create a table to store the NetFlow data
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
    if packet.haslayer(NetflowDataFlowSet):
        # Extract the required fields from the packet
        date = datetime.now().strftime('%Y-%m-%d')
        time = datetime.now().strftime('%H:%M:%S')
        router_ip = packet[IP].src
        num_packets = packet[IP].len
        source_ip = packet[IP].src
        destination_ip = packet[IP].dst
        protocol = packet[IP].proto
        source_port = packet[TCP].sport if TCP in packet else packet[UDP].sport
        destination_port = packet[TCP].dport if TCP in packet else packet[UDP].dport

        # Save the extracted fields to the database
        cursor.execute('''
            INSERT INTO netflow_data (date, time, router_ip, num_packets, source_ip, destination_ip, protocol, source_port, destination_port)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (date, time, router_ip, num_packets, source_ip, destination_ip, protocol, source_port, destination_port))
        conn.commit()
        print("Packet captured:", packet.summary())
print("NetFlow Sniffer started.")
# Start capturing NetFlow packets continuously on port 2055
sniff(filter='udp and port 2055' , prn=process_packet)





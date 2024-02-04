from scapy.all import *
import sqlite3
from datetime import datetime
from scapy.layers.snmp import SNMP
from scapy.layers.inet import IP, UDP

# Create a connection to the database
conn = sqlite3.connect('traps.db')
c = conn.cursor()

# Create a table to store trap data
c.execute('''CREATE TABLE IF NOT EXISTS snmp_traps
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              date TEXT,
              time TEXT,
              router_ip TEXT,
              trap_type TEXT,
              message TEXT,
              interface_name TEXT,
              state TEXT)''')

# Define a function to handle SNMP trap packets
def handle_trap(packet):
    if packet.haslayer(SNMP):
        trap_type = packet[SNMP].community
        if trap_type == 'SYSLOG':
            date = datetime.now().strftime('%Y-%m-%d')
            time = datetime.now().strftime('%H:%M:%S')
            router_ip = packet[IP].src
            message = packet[SNMP].varbindlist[0][1]
            c.execute("INSERT INTO snmp_traps (date, time, router_ip, trap_type, message) VALUES (?, ?, ?, ?, ?)",
                      (date, time, router_ip, trap_type, message))
        elif trap_type == 'LINK' or trap_type == 'LINEPROTO':
            date = datetime.now().strftime('%Y-%m-%d')
            time = datetime.now().strftime('%H:%M:%S')
            router_ip = packet[IP].src
            interface_name = packet[SNMP].varbindlist[0][1]
            state = packet[SNMP].varbindlist[1][1]
            c.execute("INSERT INTO snmp_traps (date, time, router_ip, trap_type, interface_name, state) VALUES (?, ?, ?, ?, ?, ?)",
                      (date, time, router_ip, trap_type, interface_name, state))
        conn.commit()
        c.execute("SELECT * FROM snmp_traps")
# Start capturing SNMP trap messages continuously
sniff(filter="udp and port 162", prn=handle_trap, iface="virbr0", store=0)

# Close the database connection
conn.close()

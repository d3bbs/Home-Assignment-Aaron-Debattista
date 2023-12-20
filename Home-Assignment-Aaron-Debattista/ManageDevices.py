import sqlite3
import ssl
import socket

def check_ip_address(ip_address):
    conn = sqlite3.connect('router_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM routers WHERE ip_address=?", (ip_address,))
    return cursor.fetchone() is None

def generate_unique_id():
    conn = sqlite3.connect('router_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(id) FROM routers")
    result = cursor.fetchone()
    return (result[0] + 1) if result[0] is not None else 1

def add_router(router_name, ip_address, username, password):
    if check_ip_address(ip_address):
        conn = sqlite3.connect('router_database.db')
        cursor = conn.cursor()
        device_id = generate_unique_id()
        cursor.execute("INSERT INTO routers VALUES (?, ?, ?, ?, ?)",
                        (device_id, router_name, ip_address, username, password))
        conn.commit()
        return "Device added successfully."
    else:
        return "IP Address already exists."

def delete_router(ip_address):
    conn = sqlite3.connect('router_database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM routers WHERE ip_address=?", (ip_address,))
    conn.commit()
    return "Device deleted successfully."

def list_routers():
    conn = sqlite3.connect('router_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM routers")
    devices = cursor.fetchall()
    devices_list = [{'id': device[0], 'router_name': device[1], 'ip_address': device[2], 'username': device[3], 'password': device[4]} for device in devices]
    return '\n'.join([f"\nID: {device['id']}\nRouter Name: {device['router_name']}\nIP Address: {device['ip_address']}\nUsername: {device['username']}\nPassword: {device['password']}\n" for device in devices_list])

def handle_request(request):
    #parts split the request into two parts, the action and the data
    parts = request.split(':', 1)
    #action is the first part of the request
    action = parts[0]
    if action == "ADD":
        #if the length of parts is not 2, then the request is invalid
        if len(parts) != 2:
            return "Invalid request."
        router_name, ip_address, username, password = parts[1].split(',')
        return add_router(router_name, ip_address, username, password)
    elif action == "DELETE":
        #same as above
        if len(parts) != 2:
            return "Invalid request."
        ip_address = parts[1]
        return delete_router(ip_address)
    elif action == "LIST":
        return list_routers()
    else:
        return "Invalid request."

def run_service():
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2
    context.load_cert_chain(certfile="server.crt", keyfile="server.key")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12345))
    server_socket.listen(1)
    print("Service running on port 12345.")

    while True:
        client_socket, client_address = server_socket.accept()
        ssl_socket = context.wrap_socket(client_socket, server_side=True)
        request = ssl_socket.recv(1024).decode()
        response = handle_request(request)
        ssl_socket.send(response.encode())
        ssl_socket.close()

if __name__ == "__main__":
    run_service()

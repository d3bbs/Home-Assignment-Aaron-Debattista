import socket
import ssl

HOST = 'localhost'  # The server's hostname or IP address
PORT = 12345        # The port used by the server

def send_request(action, data='None'):
    with socket.create_connection((HOST, PORT)) as sock:
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
while True:
    print("~~~Menu~~~")
    print("1. Add Router")
    print("2. Delete Router")
    print("3. List Router")
    print("4 Set Backup Time")
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
        send_request("ADD", [router_name, ip_address, username, password])
    elif choice == "2":
        data = input("Enter router name to delete: ")
        send_request("DELETE", [data])
    elif choice == "3":
        response = send_request("LIST", [])
    elif choice =='4':
        print("Set Backup Time")
    elif choice == "13":
        break
    else:
        print("Invalid choice. Please try again.")
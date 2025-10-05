import socket
import sys

if len(sys.argv) != 5 or sys.argv[1] != "HELLO":
    print("Usage: python TCP_client.py HELLO <Server_IP> <Server_Port> <ConnectionID>")
    sys.exit(1)

server_ip = sys.argv[2]
server_port = int(sys.argv[3])
conn_id = sys.argv[4]

tries = 0
while tries < 3:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(60)
        sock.connect((server_ip, server_port))
        sock.sendall(f"HELLO {conn_id}".encode())
        reply = sock.recv(1024).decode().strip().split()

        if reply[0] == "OK":
            print(f"Connection established {reply[1]} {reply[2]} {reply[3]}")
            sock.close()
            break
        elif reply[0] == "RESET":
            print(f"Connection Error {reply[1]}")
            conn_id = input("Enter new Connection ID: ")
            tries += 1
        sock.close()
    except socket.timeout:
        print(f"Connection Error {conn_id}")
        conn_id = input("Enter new Connection ID: ")
        tries += 1

if tries == 3:
    print("Connection Failure")

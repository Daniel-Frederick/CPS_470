import socket
import sys
import time

# Usage: python UDP_client.py HELLO Server_IP Server_Port ConnectionID
if len(sys.argv) != 5 or sys.argv[1] != "HELLO":
    print("Usage: python UDP_client.py HELLO <Server_IP> <Server_Port> <ConnectionID>")
    sys.exit(1)

server_ip = sys.argv[2]
server_port = int(sys.argv[3])
conn_id = sys.argv[4]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(10)

while True:
    try:
        sock.sendto(f"HELLO {conn_id}".encode(), (server_ip, server_port))
        data, _ = sock.recvfrom(1024)
        reply = data.decode().strip().split()

        if reply[0] == "OK":
            print(f"Connection established {reply[1]} {reply[2]} {reply[3]}")
            break
        elif reply[0] == "RESET":
            print(f"Connection Error {conn_id}")
            break

    except socket.timeout:
        print(f"Connection Failure")
        break

sock.close()

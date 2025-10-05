import socket
import sys
import time

# Usage: python UDP_server.py Server_IP Server_Port
if len(sys.argv) != 3:
    print("Usage: python UDP_server.py <Server_IP> <Server_Port>")
    sys.exit(1)

server_ip = sys.argv[1]
server_port = int(sys.argv[2])
used_ids = {}

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((server_ip, server_port))
print(f"UDP server listening on {server_ip}:{server_port}")

while True:
    data, addr = sock.recvfrom(1024)
    message = data.decode().strip().split()

    if len(message) != 2 or message[0] != "HELLO":
        continue

    conn_id = message[1]
    client_ip, client_port = addr

    # Check connection ID
    now = time.time()
    used_ids = {k: v for k, v in used_ids.items() if now - v < 60}

    if conn_id in used_ids:
        response = f"RESET {conn_id}"
    else:
        used_ids[conn_id] = now
        response = f"OK {conn_id} {client_ip} {client_port}"

    sock.sendto(response.encode(), addr)

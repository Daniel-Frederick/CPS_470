import socket
import sys
import time

if len(sys.argv) != 3:
    print("Usage: python TCP_server.py <Server_IP> <Server_Port>")
    sys.exit(1)

server_ip = sys.argv[1]
server_port = int(sys.argv[2])
used_ids = {}

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((server_ip, server_port))
sock.listen(5)
print(f"TCP server listening on {server_ip}:{server_port}")

while True:
    conn, addr = sock.accept()
    data = conn.recv(1024).decode().strip().split()
    if len(data) != 2 or data[0] != "HELLO":
        conn.close()
        continue

    conn_id = data[1]
    client_ip, client_port = addr
    now = time.time()
    used_ids = {k: v for k, v in used_ids.items() if now - v < 60}

    if conn_id in used_ids:
        response = f"RESET {conn_id}"
    else:
        used_ids[conn_id] = now
        response = f"OK {conn_id} {client_ip} {client_port}"

    conn.sendall(response.encode())
    conn.close()

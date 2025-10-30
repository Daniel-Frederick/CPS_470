# To Test, run with: `python3 teamXproxy.py 127.0.0.1`
# Enter this into browser: http://localhost:8888/gaia.cs.umass.edu/wireshark-labs/HTTP-wireshark-file2.html
# First time will miss, refresh the page and it will Hit

from socket import *
import sys
import os

# Check for valid command-line arguments
if len(sys.argv) <= 1:
    print('Usage: "python teamXproxy.py server_ip"')
    sys.exit(2)

# Get the IP address and define a port number
server_ip = sys.argv[1]
server_port = 8888  # you can change this if needed

# Create a TCP socket
tcpSerSock = socket(AF_INET, SOCK_STREAM)

# Bind the socket to the given IP and port, and start listening
tcpSerSock.bind((server_ip, server_port))
tcpSerSock.listen(5)

print(f"Proxy server running on {server_ip}:{server_port} ...")

while True:
    print('Ready to serve...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('Received a connection from:', addr)

    # Receive the request message from the client
    message = tcpCliSock.recv(4096).decode()
    if not message:
        tcpCliSock.close()
        continue

    print("Client message:\n", message)

    # Extract the requested filename
    try:
        filename = message.split()[1].partition("/")[2]
    except IndexError:
        tcpCliSock.close()
        continue

    print("Requested file:", filename)
    fileExist = False
    filetouse = filename

    try:
        # Check whether the file exists in the cache
        if os.path.isfile(filetouse):
            fileExist = True
            print("Cache hit: serving from local file", filetouse)
            with open(filetouse, "rb") as f:
                outputdata = f.read()

            # Send HTTP response header and cached data
            tcpCliSock.send(b"HTTP/1.0 200 OK\r\n")
            tcpCliSock.send(b"Content-Type:text/html\r\n\r\n")
            tcpCliSock.send(outputdata)
            print("Served from cache successfully.")
        else:
            raise IOError

    except IOError:
        # Cache miss: need to fetch from web server
        if not fileExist:
            print("Cache miss. Fetching from origin server...")

            # Extract host name (remove 'http://' and 'www.')
            hostn = filename.replace("www.", "", 1)
            hostn = hostn.split("/")[0]
            resource = filename.partition("/")[2]

            try:
                # Create a socket to connect to the web server
                c = socket(AF_INET, SOCK_STREAM)
                c.connect((hostn, 80))
                print("Connected to origin:", hostn)

                # Send GET request to origin server
                request_line = f"GET /{resource} HTTP/1.0\r\nHost: {hostn}\r\n\r\n"
                c.sendall(request_line.encode())

                # Read the response from origin server
                response = b""
                while True:
                    data = c.recv(4096)
                    if len(data) > 0:
                        response += data
                    else:
                        break

                # Send response to client
                tcpCliSock.sendall(response)

                # Write response to cache file
                os.makedirs(os.path.dirname(filetouse), exist_ok=True)
                with open(filetouse, "wb") as tmpFile:
                    tmpFile.write(response)

                print("Response cached and forwarded to client.")

                c.close()

            except Exception as e:
                print("Error fetching from origin:", e)
                tcpCliSock.send(b"HTTP/1.0 404 Not Found\r\n\r\n")
                tcpCliSock.send(b"<html><body><h1>404 Not Found</h1></body></html>")
        else:
            # File not found (should rarely reach here)
            tcpCliSock.send(b"HTTP/1.0 404 Not Found\r\n\r\n")
            tcpCliSock.send(b"<html><body><h1>404 Not Found</h1></body></html>")

    tcpCliSock.close()

tcpSerSock.close()

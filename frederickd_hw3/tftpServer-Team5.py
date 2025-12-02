"""
CPS470 - Spring 2025
Team: 5
Names: Erich and Daniel

A Trivial File Transfer Protocol Server
"""

import socket
import os
import math
import struct

TFTP_PORT = 69
TFTP_BLOCK_SIZE = 512
MAX_UDP_PACKET_SIZE = 65535

# Maximum block number before rollover (RFC recommends modulo 65536)
BLOCK_LIMIT = 65535  

def main():
    client_socket = socket_setup()
    print("Server is ready to receive a request")

    # -------------------------------
    # Receive the initial RRQ request
    # -------------------------------

    request, client_addr = client_socket.recvfrom(MAX_UDP_PACKET_SIZE)

    opcode = struct.unpack("!H", request[0:2])[0]
    if opcode == 5:
        handle_client_error(request)
        return

    if opcode != 1:  # RRQ only
        send_error(client_socket, client_addr, 4, b"Illegal TFTP operation")
        return

    filename, mode = parse_rrq(request)
    print(f"Client requested: {filename} (mode={mode})")

    # Verify file exists
    if not os.path.exists(filename):
        send_error(client_socket, client_addr, 1, b"File not found")
        return

    # --------------------------------
    # Begin sending file block-by-block
    # --------------------------------
    send_file(client_socket, client_addr, filename)


# --------------------------------------------------------------
# RRQ PARSING
# --------------------------------------------------------------
def parse_rrq(packet):
    parts = packet[2:].split(b"\x00")
    filename = parts[0].decode()
    mode = parts[1].decode().lower()  # "octet" (binary) or "netascii"
    return filename, mode


# --------------------------------------------------------------
# SENDING THE FILE BLOCK-BY-BLOCK
# --------------------------------------------------------------
def send_file(sock, addr, filename):
    total_blocks = get_file_block_count(filename)

    file = open(filename, "rb")  # Optimized: open only once

    block_number = 1
    last_ack = 0

    while True:
        # Roll over block number if needed
        if block_number > BLOCK_LIMIT:
            block_number = 0

        # Seek to appropriate file position
        file.seek((block_number - 1) * TFTP_BLOCK_SIZE)
        data = file.read(TFTP_BLOCK_SIZE)

        # Construct DATA packet
        packet = struct.pack("!HH", 3, block_number) + data

        print(f"[SERVER] Sending block {block_number}")
        sock.sendto(packet, addr)

        # Wait for ACK
        try:
            ack_packet, _ = sock.recvfrom(MAX_UDP_PACKET_SIZE)
        except:
            continue

        ack_opcode, ack_block = struct.unpack("!HH", ack_packet[:4])

        if ack_opcode == 5:
            handle_client_error(ack_packet)
            return

        print(f"[SERVER] Received ACK for block {ack_block}")

        if ack_block == last_ack:  
            # Duplicate ACK → resend block_number
            print("[SERVER] Duplicate ACK detected → Resending block")
            continue

        if ack_block == block_number:
            last_ack = ack_block
            block_number += 1

        # If this was the final block (<512 bytes), transfer ends
        if len(data) < 512:
            print("[SERVER] Final block acknowledged. Closing connection.")
            file.close()
            return


# --------------------------------------------------------------
# ERROR HANDLING
# --------------------------------------------------------------
def send_error(sock, addr, error_code, msg_bytes):
    packet = struct.pack("!HH", 5, error_code) + msg_bytes + b"\x00"
    sock.sendto(packet, addr)
    print(f"[SERVER] Sent ERROR {error_code}: {msg_bytes.decode()}")


def handle_client_error(packet):
    opcode, errcode = struct.unpack("!HH", packet[:4])
    msg = packet[4:-1].decode()
    print(f"[CLIENT ERROR] Code {errcode}: {msg}")
    print("Closing server.")


# --------------------------------------------------------------
# REQUIRED HELPER FUNCTIONS
# --------------------------------------------------------------
def get_file_block_count(filename):
    try:
        size = os.stat(filename).st_size
        return math.ceil(size / TFTP_BLOCK_SIZE)
    except:
        return -1


def socket_setup():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', TFTP_PORT))
    return s


# --------------------------------------------------------------
main()


# chat room client

import socket
from based import data_encapsulate, unpack_header, HEADER_SIZE, ENCODER

# constants
SERVER_IP   = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 12345



# TCP/IP client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))

header = client_socket.recv(HEADER_SIZE)
payload_length = unpack_header(header)

payload = client_socket.recv(payload_length)
print(payload.decode(ENCODER))


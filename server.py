# chat room server

import socket
from based import data_encapsulate, unpack_header 

# constants
HOST_IP     = socket.gethostbyname(socket.gethostname())
HOST_PORT   = 12345
ENCODER     = 'utf-8'

# TCP/IP server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST_IP, HOST_PORT))
server_socket.listen()

client_socket, client_address = server_socket.accept()

message = data_encapsulate('Hello, welcome to the server')
client_socket.send(message)



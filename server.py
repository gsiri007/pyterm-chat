# chat room server

import socket
import queue
import threading
from based import HEADER_SIZE, data_encapsulate, unpack_header 

# constants
HOST_IP     = socket.gethostbyname(socket.gethostname())
HOST_PORT   = 12345
ENCODER     = 'utf-8'

# TCP/IP server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST_IP, HOST_PORT))
server_socket.listen()

# log messages queue
log_messages_queue = queue.Queue()

# broadcast messages queue
broadcast_messages_queue = queue.Queue()

# store client information
client_sockets   = []
client_addresses = []
client_names     = []

# print log messages to stdout
def log_messages() -> None:
    while True:
        message = log_messages_queue.get()
        print(message)

# send messages to clients
def broadcast_messages() -> None:
    while True:
        #TODO:
        pass

def receive_messages() -> None:
    pass

def connect_client() -> None:
    while True:
        # accept client connection 
        client_socket, client_address = server_socket.accept()

        # store client socket and address
        client_sockets.append(client_socket)
        client_addresses.append(client_address)

        # send 'NAME' flag requesting client name
        flag = data_encapsulate('NAME')
        client_socket.send(flag)

        # capture the client name
        header = client_socket.recv(HEADER_SIZE)
        payload_length = unpack_header(header)
        client_name = client_socket.recv(payload_length)

        # store client name
        client_names.append(client_name)

        # log client connection successful
        log_message = f'client {client_address} connected.'
        log_messages_queue.put(log_message)

        # broadcast to clients about new connection
        broadcast_message = f'SERVER: {client_name} joined the chat room|SERVER'
        broadcast_messages_queue.put(broadcast_message)

        # thread dedicated to receiving messages from client
        receiving_thread = threading.Thread(
                target=receive_messages, 
                args=(client_socket,)
            )
        receiving_thread.start()

# logging thread
logging_thread = threading.Thread(target=log_messages)
logging_thread.start()

# broadcasting thread
broadcasting_thread = threading.Thread(target=broadcast_messages)
broadcasting_thread.start()

connect_client()

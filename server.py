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
broadcast_processing_queue = queue.Queue()

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
        # process the broadcast message into message and sender
        message_to_process = broadcast_processing_queue.get()
        message, sender = message_to_process.split('|')

        # broadcast the message to every client
        if sender == 'SERVER':
            for client_socket in client_sockets:
                payload = data_encapsulate(message)
                client_socket.send(payload)
        else:
            # skips the sender and broadcast message to clients
            for client_socket in client_sockets:
                # lookup client name 
                index = client_sockets.index(client_socket)
                client_name = client_sockets[index]

                if client_name != sender:
                    payload = data_encapsulate(message)
                    client_socket.send(payload)


# logging thread
logging_thread = threading.Thread(target=log_messages)

# broadcasting thread
broadcasting_thread = threading.Thread(target=broadcast_messages)


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
        broadcast_processing_queue.put(broadcast_message)

        # thread dedicated to receiving messages from client
        receiving_thread = threading.Thread(
                target=receive_messages, 
                args=(client_socket,)
            )
        receiving_thread.start()


def receive_messages(client_socket: socket.socket) -> None:
    while True:
        try:
            # get client message
            header = client_socket.recv(HEADER_SIZE)
            payload_length = unpack_header(header)
            payload = client_socket.recv(payload_length)

            # lookup client name 
            index = client_sockets.index(client_socket)
            client_name = client_sockets[index]

            message = payload.decode(ENCODER)

            if message == '\\exit':
                # kill client connection and receiving thread
                disconnect_client(client_socket)
                break

            # format and broadcast client message
            broadcast_message = f'{client_name}: {message}|{client_name}'
            broadcast_processing_queue.put(broadcast_message)

        except Exception as e:
            # log error
            error_message = f'ERROR (receive messages): {e}'
            log_messages_queue.put(error_message)
            
            # kill client connection and receiving thread
            disconnect_client(client_socket) 
            break


def disconnect_client(client_socket: socket.socket) -> None:
    # lookup client details 
    index = client_sockets.index(client_socket)
    client_address = client_addresses[index]
    client_name = client_sockets[index]

    # remove client details
    client_sockets.remove(client_socket)
    client_addresses.remove(client_address)
    client_names.remove(client_name)

    # close client socket
    client_socket.close()

    # log client disconnected
    log_message = f'client {client_address} disconnected.'
    log_messages_queue.put(log_message)

    # broadcast client disconnected
    broadcast_messsage = f'SERVER: {client_name} left the chat room|SERVER'
    broadcast_processing_queue.put(broadcast_messsage)


if __name__ == '__main__':
    logging_thread.start()
    broadcasting_thread.start()
    connect_client()

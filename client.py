# chat room client

import socket
import sys
import threading
import queue
from based import data_encapsulate, unpack_header, HEADER_SIZE, ENCODER

# constants
SERVER_IP   = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 12345

# TCP/IP client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))

# message queue to write output to console
output_message_queue = queue.Queue()

# connection closing event
disconnect_event = threading.Event()

def write_output() -> None:
    while not disconnect_event.is_set():
        message = output_message_queue.get()
        print(message)

def receive_messages() -> None:
    while not disconnect_event.is_set():
        try:
            # get payload length
            header = client_socket.recv(HEADER_SIZE)
            payload_length = unpack_header(header)
            
            # receive message from server and decode
            message = client_socket.recv(payload_length)
            message = message.decode(ENCODER)

            if message == 'NAME':
                # send client name to server if 'NAME' flag received
                client_name = input('Enter your name: ')
                data = data_encapsulate(client_name)
                client_socket.send(data)

            else: 
                # push message to output queue
                output_message_queue.put(message)

        except Exception as e:
            error_message = f'ERROR (receive message): {e}'
            client_disconnect()

def send_messages() -> None:
    while not disconnect_event.is_set():
        message = input('') 
        data = data_encapsulate(message)
        client_socket.send(data)

        if message == '\\exit':
            output_message_queue.put('--- disconnecting ---')
            client_disconnect()

def client_disconnect() -> None:
    client_socket.close()
    disconnect_event.set()
    sys.exit(0)


output_writing_thread = threading.Thread(target=write_output)
receiving_thread = threading.Thread(target=receive_messages)
sending_thread = threading.Thread(target=send_messages)

if __name__ == '__main__':
    output_writing_thread.start()
    receiving_thread.start()
    sending_thread.start()
    

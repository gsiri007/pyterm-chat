import socket
import struct 

ENCODER     = 'utf-8'
HEADER_SIZE = 4

def data_encapsulate(data: str ) -> bytes:
    payload = data.encode(ENCODER)
    payload_length = len(payload)
    header = struct.pack('!I', payload_length)

    return header + payload

def unpack_header(header: bytes) -> int:
    return struct.unpack('!I', header)[0]




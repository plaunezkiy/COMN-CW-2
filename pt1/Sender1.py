# Nikita Peleshatyi 2150635
import socket
import time
import sys


class Sender:
    PACKET_DATA_SIZE = 1024
    address = None
    sock = None
    
    def __init__(self, host="127.0.0.1", port=5005):
        self.address = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def compose_and_send_packet(self, seq_number: int, data: bytes, eof: bool=False):
        SEQ_NUMBER = seq_number.to_bytes(2, 'big')
        EOF = eof.to_bytes(1, 'big')
        header = SEQ_NUMBER + EOF
        ###
        packet = header + data
        self.sock.sendto(packet, self.address)
        time.sleep(0.001)
    
    def send_file(self, filename):
        with open(filename, 'rb') as fbytes:
            seq_counter = 0
            while True:
                chunk = fbytes.read(self.PACKET_DATA_SIZE)
                # final chunk will have less than 1024B of data
                # if reached the end, send EoF packet
                if len(chunk) < self.PACKET_DATA_SIZE:
                    self.compose_and_send_packet(seq_counter, chunk, True)
                    break
                self.compose_and_send_packet(seq_counter, chunk)
                # next chunk
                seq_counter += 1


# RemoteHost, Port, Filename
host = sys.argv[1]
port = int(sys.argv[2])
fname = sys.argv[3]
sender = Sender(host, port)
sender.send_file(fname)


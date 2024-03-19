# Implement sender and receiver endpoints for transferring a large file given (test.jpg) 
# from the sender to the receiver on localhost over UDP as
# a sequence of small messages with 1KB maximum payload (NB. 1KB = 1024 bytes) via
# the loopback interface

#  python3 Sender1.py <RemoteHost> <Port> <Filename>
import socket

msg_size = 1027 # bytes (3B header + 1024B data)
# header - 2B seq number, 1B end-of-file EoF flag
class Sender:
    PACKET_DATA_SIZE = 1024
    address = None
    sock = None
    
    def __init__(self, host="127.0.0.1", port=5005):
        self.address = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.sock.bind((host, port))
    
    def compose_and_send_packet(self, seq_number: int, data: bytes, eof: bool=False):
        SEQ_NUMBER = seq_number.to_bytes(2, 'big')
        EOF = eof.to_bytes(1, 'big')
        header = SEQ_NUMBER + EOF
        ###
        packet = header + data
        self.sock.sendto(packet, self.address)
    
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
                # exit()
                # next chunk
                seq_counter += 1


sender = Sender()
sender.send_file("test.jpg")


# Implement sender and receiver endpoints for transferring a large file given (test.jpg) 
# from the sender to the receiver on localhost over UDP as
# a sequence of small messages with 1KB maximum payload (NB. 1KB = 1024 bytes) via
# the loopback interface

#  python3 Sender2.py <RemoteHost> <Port> <Filename>
import socket


msg_size = 1027 # bytes (3B header + 1024B data)
# header - 2B seq number, 1B end-of-file EoF flag
class Sender:
    PACKET_DATA_SIZE = 1024
    ACK_SIZE = 2
    address = None
    sock = None
    
    def __init__(self, host="127.0.0.1", port=5005, retry_timeout=3):
        self.address = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # enable immediate address reusage (for sending+receiving)
        self.sock.settimeout(retry_timeout)
        # self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.sock.bind(self.address)

    def get_ack_seq_num(self, packet):
        seq_num = int.from_bytes(packet, 'big')
        return seq_num
    
    def receive_data(self, buffsize):
        data, addr = self.sock.recvfrom(buffsize)
        return data
    
    def compose_and_send_packet(self, seq_number: int, data: bytes, eof: bool=False):
        # compose packet
        SEQ_NUMBER = seq_number.to_bytes(self.ACK_SIZE, 'big')
        EOF = eof.to_bytes(1, 'big')
        header = SEQ_NUMBER + EOF
        packet = header + data
        # send/resend packet loop (waiting for ACK)
        while True:
            self.sock.sendto(packet, self.address)
            try:
                # wait for ACK
                pckt, addr = self.sock.recvfrom(self.ACK_SIZE)
                ack = self.get_ack_seq_num(pckt)
                if ack == seq_number:
                    break
            except socket.timeout:
                print("Timed out, resending")
                continue
            # # if received and matches, move on
            # if ackReceived and self.get_ack_seq_num(ack) == SEQ_NUMBER:
            #     correctAckReceived = True
            # else:
            #     # retransmit
                # self.sock.sendto(packet, self.address)
    
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


# RemoteHost, Port, Filename, Timeout
sender = Sender()

sender.send_file("test.jpg")


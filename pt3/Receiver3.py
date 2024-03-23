# Nikita Peleshatyi 2150635
import socket
import sys


class Receiver:
    PACKET_DATA_SIZE = 1024
    PACKET_HEADER_SIZE = 3
    ACK_SIZE = 2
    address = None
    sock = None

    @property
    def buffsize(self):
        return self.PACKET_DATA_SIZE + self.PACKET_HEADER_SIZE

    def __init__(self, host="127.0.0.1", port=5005):
        self.address = (host, port)
        # print(f"Listening on {self.address}")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.address)
        # self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    def make_ack_packet(self, seq_number: int):
        return seq_number.to_bytes(self.ACK_SIZE, 'big')

    def send_ack(self, seq_number: int, address):
        ack = self.make_ack_packet(seq_number)
        self.sock.sendto(ack, address)
    
    def receive_data(self):
        data, addr = self.sock.recvfrom(self.buffsize)
        return data
    
    def receive_file(self, filename):
        with open(filename, "wb") as file:
            while True:
                data, addr = self.sock.recvfrom(self.buffsize)
                if data:
                    # parse data
                    header = data[:3]
                    seq_number = int.from_bytes(header[:2], 'big')
                    eof = bool.from_bytes(header[-1:], 'big')
                    payload = data[3:]
                    # deliver data
                    file.write(payload)
                    # send ACK
                    self.send_ack(seq_number, addr)
                    if eof:
                        break


# Port, Filename
port = int(sys.argv[1])
fname = sys.argv[2]

receiver = Receiver(port=port)
receiver.receive_file(fname)

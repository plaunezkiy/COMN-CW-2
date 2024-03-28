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

    def __init__(self, host="127.0.0.1", port=5005, window_size=1):
        self.address = (host, port)
        self.window_size = window_size
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.address)
    
    def make_ack_packet(self, seq_number: int):
        return seq_number.to_bytes(self.ACK_SIZE, 'big')

    def send_ack(self, seq_number: int, address):
        ack = self.make_ack_packet(seq_number)
        self.sock.sendto(ack, address)
    
    def receive_data(self):
        data, addr = self.sock.recvfrom(self.buffsize)
        return data
    
    def receive_file(self, filename):
        pkts_received = set()
        base = -1
        EOF = False
        # keys are seq_nums, values are packet payload
        window_buffer = {}
        with open(filename, "wb") as file:
            while True:
                data, addr = self.sock.recvfrom(self.buffsize)
                if data:
                    # parse data
                    header = data[:3]
                    seq_number = int.from_bytes(header[:2], 'big')
                    # send ACK
                    self.send_ack(seq_number, addr)
                    eof = bool.from_bytes(header[-1:], 'big')
                    if eof:
                        # if final packet has arrived, take a note - ready to terminate
                        EOF = True
                    # in order
                    if base < seq_number <= base + self.window_size:                    
                        # print(window_buffer.keys(), file=sys.stderr)
                        # print(f"Received & Buffered: {seq_number}", file=sys.stderr)
                        payload = data[3:]
                        if seq_number not in pkts_received:
                            pkts_received.add(seq_number)
                            window_buffer[seq_number] = payload
                    # deliver data if available
                    while base + 1 in window_buffer.keys():
                        # print(f"Delivered: {base+1}", EOF, file=sys.stderr)
                        file.write(window_buffer[base + 1])
                        del window_buffer[base + 1]
                        base += 1
                    if EOF and len(window_buffer) == 0:
                        # in case final ack gets lost
                        self.send_ack(seq_number, addr)
                        break


# Port, Filename, WindowSize
port = int(sys.argv[1])
fname = sys.argv[2]
window_size = int(sys.argv[3])

receiver = Receiver(port=port, window_size=window_size)
receiver.receive_file(fname)

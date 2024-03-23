# Nikita Peleshatyi 2150635
import socket
import time
import sys
import errno
import select


class Sender:
    PACKET_DATA_SIZE = 1024
    ACK_SIZE = 2
    address = None
    sock = None
    
    def __init__(self, host="127.0.0.1", port=5005, retry_timeout=5, window_size=1):
        self.address = (host, port)
        self.window_size = window_size
        # print(f"Sending to {self.address}")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(retry_timeout/1000)
        self.sock.setblocking(False)
        # enable immediate address reusage (for sending+receiving)
        # self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.sock.bind(self.address)

    def get_ack_seq_num(self, packet):
        seq_num = int.from_bytes(packet, 'big')
        return seq_num
    
    def receive_data(self, buffsize):
        data, addr = self.sock.recvfrom(buffsize)
        return data
    
    def compose_and_send_packet(self, seq_number: int, data: bytes, eof: bool=False):
        print(f"Sending: {seq_number}")
        # compose packet
        SEQ_NUMBER = seq_number.to_bytes(self.ACK_SIZE, 'big')
        EOF = eof.to_bytes(1, 'big')
        header = SEQ_NUMBER + EOF
        packet = header + data
        
        try:
            self.sock.sendto(packet, self.address)
        except socket.error as e:
            if e.errno != errno.EAGAIN:
                raise e
            select.select([], [self.sock], [])
    
    # def send_data(self, data):
    #     return
    
    def send_file(self, filename):
        self.retransmissions = 0
        with open(filename, 'rb') as fbytes:
            file_data = fbytes.read()
            fsize = len(file_data)
            # 
            seq_counter = 0
            eof = False
            base = -1
            nextseqnum = 0
            # 
            start = time.time()
            while not eof:
                readable, writable, _ = select.select([self.sock], [self.sock], [], 0)
                while seq_counter <= base + self.window_size:
                    # print(seq_counter, file=sys.stderr)
                    start = seq_counter * self.PACKET_DATA_SIZE
                    chunk = file_data[start : start+self.PACKET_DATA_SIZE]
                    # seq number is limited to 2 bytes, which is FF_FF = 256^2 = 65536
                    R_SEQ_NUMBER = seq_counter % (256 ** self.ACK_SIZE)

                    # final chunk will have less than 1024B of data
                    # if reached the end, send EoF packet
                    if len(chunk) < self.PACKET_DATA_SIZE:
                        eof = True
                    self.compose_and_send_packet(R_SEQ_NUMBER, chunk, eof)
                    if eof:
                        end = time.time()
                        break
                    # next chunk
                    seq_counter += 1
                if self.sock in readable:
                    try:
                        pckt, addr = self.sock.recvfrom(self.ACK_SIZE)
                        base = self.get_ack_seq_num(pckt)
                    except socket.timeout:
                        seq_counter = base + 1
        runtime = end - start
        # print(runtime, fsize/1000)
        throughput = (fsize / 1000) / runtime
        print(f"{runtime}#{self.retransmissions}#{throughput}")


# RemoteHost, Port, Filename, Timeout
host = sys.argv[1]
port = int(sys.argv[2])
fname = sys.argv[3]
timeout = int(sys.argv[4])
window_size = int(sys.argv[5])

sender = Sender(host, port, timeout, window_size)
sender.send_file(fname)


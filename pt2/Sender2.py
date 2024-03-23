# Nikita Peleshatyi 2150635
import socket
import time
import sys


class Sender:
    PACKET_DATA_SIZE = 1024
    ACK_SIZE = 2
    address = None
    sock = None
    
    def __init__(self, host="127.0.0.1", port=5005, retry_timeout=5):
        self.address = (host, port)
        # print(f"Sending to {self.address}")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(retry_timeout/1000)
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
        # compose packet
        # seq number is limited to 2 bytes, which is FF_FF = 256^2 = 65536
        R_SEQ_NUMBER = seq_number % (256 ** self.ACK_SIZE)
        SEQ_NUMBER = R_SEQ_NUMBER.to_bytes(self.ACK_SIZE, 'big')
        EOF = eof.to_bytes(1, 'big')
        header = SEQ_NUMBER + EOF
        packet = header + data
                
        # send/resend packet loop (waiting for ACK)
        pkt_retransmissions = 0
        while True:
            self.sock.sendto(packet, self.address)
            try:
                # wait for ACK
                pckt, addr = self.sock.recvfrom(self.ACK_SIZE)
                ack_no = self.get_ack_seq_num(pckt)
                # since the original number is %'ed
                if ack_no == R_SEQ_NUMBER:
                    break
            except socket.timeout:
                # if the final is ack is not there after 10 retries (10 x Timeout)
                # the receiver has likely terminated, so should the sender
                if eof and pkt_retransmissions >= 10:
                    print("No EoF ACK received after 10 retries, terminating...", file=sys.stderr)
                    break
                pkt_retransmissions += 1
                # print(f"Resend: {seq_number}", file=sys.stderr)
                continue
        self.retransmissions += pkt_retransmissions
    
    def send_file(self, filename):
        self.retransmissions = 0
        fsize = 0
        with open(filename, 'rb') as fbytes:
            seq_counter = 0
            start = time.time()
            while True:
                # print(seq_counter, file=sys.stderr)
                chunk = fbytes.read(self.PACKET_DATA_SIZE)
                # record the size of the file
                fsize += len(chunk)
                # final chunk will have less than 1024B of data
                # if reached the end, send EoF packet
                if len(chunk) < self.PACKET_DATA_SIZE:
                    self.compose_and_send_packet(seq_counter, chunk, True)
                    end = time.time()
                    break
                # otherwise, continue sequence
                self.compose_and_send_packet(seq_counter, chunk)
                # next chunk
                seq_counter += 1
        runtime = end - start
        # print(runtime, fsize/1000)
        throughput = (fsize / 1000) / runtime
        print(f"{runtime}#{self.retransmissions}#{throughput}")


# RemoteHost, Port, Filename, Timeout
host = sys.argv[1]
port = int(sys.argv[2])
fname = sys.argv[3]
timeout = int(sys.argv[4])

sender = Sender(host, port, timeout)
sender.send_file(fname)


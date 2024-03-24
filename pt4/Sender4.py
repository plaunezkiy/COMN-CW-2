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
    data = None
    
    def __init__(self, host="127.0.0.1", port=5005, retry_timeout=5, window_size=1):
        self.address = (host, port)
        self.window_size = window_size
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.timeout = retry_timeout/1000
        self.sock.settimeout(self.timeout)
        self.sock.setblocking(False)

    @property
    def num_packets(self):
        fsize = len(self.data)
        return (fsize // self.PACKET_DATA_SIZE) + (fsize % self.PACKET_DATA_SIZE == 0)

    @property
    def max_seq_number(self):
        return (256 ** self.ACK_SIZE)

    def get_ack_seq_num(self, packet):
        seq_num = int.from_bytes(packet, 'big')
        return seq_num
    
    def receive_data(self, buffsize):
        data, addr = self.sock.recvfrom(buffsize)
        return data
    
    def compose_and_send_packet(self, seq_number: int):
        print(f"Sending: {seq_number}", file=sys.stderr)
        # compose packet
        R_SEQ_NUMBER = seq_number % self.max_seq_number
        SEQ_NUMBER = R_SEQ_NUMBER.to_bytes(self.ACK_SIZE, 'big')
        eof = seq_number == self.num_packets
        EOF = eof.to_bytes(1, 'big')
        header = SEQ_NUMBER + EOF
        start = seq_number * self.PACKET_DATA_SIZE
        # seq number is limited to 2 bytes, which is FF_FF = 256^2 = 65536
        data = self.data[start : start+self.PACKET_DATA_SIZE]
        packet = header + data
        
        self.sock.sendto(packet, self.address)
    
    def send_file(self, filename):
        self.retransmissions = 0
        with open(filename, 'rb') as fbytes:
            self.data = fbytes.read()            
            # 
            seq_counter = 0
            base = -1
            acks_received = set()
            timers = {}
            window = []
            # 
            start = time.time()
            
            while seq_counter <= self.num_packets:
                readable, writable, _ = select.select([self.sock], [self.sock], [], self.timeout)
                #                        -1          5
                while seq_counter <= base + self.window_size: # and self.sock in writable:
                    print(len(window))
                    # if base == seq_counter - 1:
                    #     timer = time.time()
                    self.compose_and_send_packet(seq_counter)
                    timers[seq_counter] = time.time()
                    window.append(seq_counter)
                    # eof
                    if seq_counter == self.num_packets:
                        end = time.time()
                    # next chunk
                    seq_counter += 1
                if self.sock in readable:
                    pckt, addr = self.sock.recvfrom(self.ACK_SIZE)
                    ack_num = self.get_ack_seq_num(pckt)
                    print(f"ACK: {ack_num}", file=sys.stderr)
                    timers[ack_num] = None
                    # add to acks
                    acks_received.add(ack_num)
                    # if base of the window, drop
                    while window[0] % self.max_seq_number in acks_received:
                        base += 1
                        window.pop(0)

                for pkt_num, pkt_timer in timers.items():
                    if pkt_timer and time.time() - pkt_timer >= self.timeout:
                        # seq_counter = base + 1
                        print(f"Timing out for: {pkt_num}", file=sys.stderr)
                        self.compose_and_send_packet(pkt_num)
                        timers[pkt_num] = time.time()
                
        runtime = end - start
        # print(runtime, fsize/1000)
        throughput = (len(self.data) / 1000) / runtime
        print(f"{runtime}#{self.retransmissions}#{throughput}")


# RemoteHost, Port, Filename, Timeout
host = sys.argv[1]
port = int(sys.argv[2])
fname = sys.argv[3]
timeout = int(sys.argv[4])
window_size = int(sys.argv[5])

sender = Sender(host, port, timeout, window_size)
sender.send_file(fname)


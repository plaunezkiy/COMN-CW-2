# Nikita Peleshatyi 2150635
import socket
import time
import sys
import select


class Sender:
    PACKET_DATA_SIZE = 1024
    ACK_SIZE = 2
    address = None
    sock = None
    
    def __init__(self, host="127.0.0.1", port=5005, retry_timeout=5, window_size=1):
        self.address = (host, port)
        self.window_size = window_size
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.timeout = retry_timeout/1000
        self.sock.settimeout(self.timeout)
        self.sock.setblocking(False)

    def get_ack_seq_num(self, packet):
        seq_num = int.from_bytes(packet, 'big')
        return seq_num
    
    def receive_data(self, buffsize):
        data, addr = self.sock.recvfrom(buffsize)
        return data
    
    def compose_and_send_packet(self, seq_number: int, data: bytes, eof: bool=False):
        # print(f"Sending: {seq_number}", file=sys.stderr)
        # compose packet
        SEQ_NUMBER = seq_number.to_bytes(self.ACK_SIZE, 'big')
        EOF = eof.to_bytes(1, 'big')
        header = SEQ_NUMBER + EOF
        packet = header + data
        
        self.sock.sendto(packet, self.address)
    
    def send_file(self, filename):
        self.retransmissions = 0
        with open(filename, 'rb') as fbytes:
            file_data = fbytes.read()
            fsize = len(file_data)
            num_packets = (fsize // self.PACKET_DATA_SIZE) + (fsize % self.PACKET_DATA_SIZE != 0)
            # 
            seq_counter = 0
            eof = False
            base = -1
            next_ack_num = 0
            timer = None
            # 
            start_timer = time.time()
            while not eof:
                readable, writable, _ = select.select([self.sock], [self.sock], [], self.timeout)
                # if there's room, send more packets
                while seq_counter <= base + self.window_size and seq_counter <= num_packets and self.sock in writable:
                    if base == seq_counter - 1:
                        timer = time.time()

                    # print(seq_counter, file=sys.stderr)
                    start = seq_counter * self.PACKET_DATA_SIZE
                    chunk = file_data[start : start+self.PACKET_DATA_SIZE]
                    # seq number is limited to 2 bytes, which is FF_FF = 256^2 = 65536
                    R_SEQ_NUMBER = seq_counter % (256 ** self.ACK_SIZE)
                    self.compose_and_send_packet(R_SEQ_NUMBER, chunk, seq_counter==num_packets)
                    # next chunk
                    seq_counter += 1
                # try receiving acks
                if self.sock in readable:
                    pckt, addr = self.sock.recvfrom(self.ACK_SIZE)
                    ack_num = self.get_ack_seq_num(pckt)
                    # print(f"ACK: {ack_num}", file=sys.stderr)
                    if ack_num >= next_ack_num:
                        # if received final packet: terminate
                        if ack_num == num_packets:
                            eof = True
                            end_timer = time.time()
                            break

                        next_ack_num = ack_num + 1
                        base = ack_num
                        # if no other packets have been sent beyond seq_number, clear timer
                        if base == seq_counter + 1:
                            timer = None
                        # otherwise reset and wait for another ack
                        else:
                            timer = time.time()
                if timer and time.time() - timer >= self.timeout:
                    seq_counter = base + 1
                    timer = None
                    # print(f"Timing out, base: {seq_counter}", file=sys.stderr)
                
        runtime = end_timer - start_timer
        throughput = (fsize / 1000) / runtime
        print(f"{throughput}")


# RemoteHost, Port, Filename, Timeout, WindowSize
host = sys.argv[1]
port = int(sys.argv[2])
fname = sys.argv[3]
timeout = int(sys.argv[4])
window_size = int(sys.argv[5])

sender = Sender(host, port, timeout, window_size)
sender.send_file(fname)


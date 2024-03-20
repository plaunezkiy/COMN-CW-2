# Nikita Peleshatyi 2150635
import socket

class Receiver:
    PACKET_DATA_SIZE = 1024
    ACK_SIZE = 2
    PACKET_HEADER_SIZE = 3
    address = None
    sock = None

    @property
    def buffsize(self):
        return self.PACKET_DATA_SIZE + self.PACKET_HEADER_SIZE

    def __init__(self, host="127.0.0.1", port=5005):
        self.address = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.address)
    
    def receive_data(self):
        data, addr = self.sock.recvfrom(self.buffsize)
        return data
    
    def receive_file(self, filename):
        with open(filename, "wb") as file:
            # keep listening
            while True:
                # try to receive data
                data = self.receive_data()
                # if data present, parse and deliver
                if data:
                    # parse data
                    header = data[:3]
                    seq_number = header[:2]
                    eof = bool.from_bytes(header[-1:], 'big')
                    payload = data[3:]
                    # deliver data
                    file.write(payload)
                    if eof:
                        break


receiver = Receiver()
receiver.receive_file("recv.jpg")

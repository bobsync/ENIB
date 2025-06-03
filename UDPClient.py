import socket
import threading
from collections import deque

class UDPClient:
    def __init__(self, ip_whiteboard):
        self.ip_whiteboard = ip_whiteboard
        self.port = 11000
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.message_queue = deque(maxlen=10)
        self.remote_ep = (self.ip_whiteboard, self.port)
        self.s.connect(self.remote_ep)
        self.receive_thread = threading.Thread(target=self.receive_packets)
        self.receive_thread.daemon = True  # Daemonize the thread
        self.receive_thread.start()
    
    def receive_packets(self):
        """Receive continuously the messages and puts them in a message queue"""
        while True:
            try:
                data, addr = self.s.recvfrom(10000)
                if data:
                    message = data.decode("utf-8")
                    self.message_queue.appendleft(message)
            except Exception as e:
                pass
    
    def get_received_messages(self):
        """Returns the content of the message queue as a dict
        only the most recent message of a topic is in this dict
        """
        received_messages = dict()
        while len(self.message_queue) > 0:
            message = self.message_queue.pop()
            sep_idx = message.index(":")
            topic = message[:sep_idx]
            content = message[sep_idx+1:]
            received_messages[topic] = content
        
        return received_messages

    
    def send(self, data):
        """Sends the string "data" to the WhiteBoard"""
        self.s.send(bytes(data, "utf-8"))


    def close(self):
        self.s.close()
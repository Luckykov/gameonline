from serverTCP import *
from serverUDP import *
import threading
from terminal import Terminal
import socket

terminal = Terminal()
tcp = ServerTCP(terminal)
udp = ServerUDP(terminal)
terminal.setServer(tcp)

print(socket.gethostbyname(socket.gethostname()))

def start():
    udp.start()

if __name__ == "__main__":
    udpThread = threading.Thread(target=start, args=(), daemon=True)
    udpThread.start()
    tcp.start()
    udpThread.join()

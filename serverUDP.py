import socket
import select
import time

class ServerUDP:
	def __init__(self, terminal):
		self.host = "127.0.0.1"
		self.port = 7172
		self.buffersize = 1024
		self.connectionLossTimeout = 5.0
		self.tickRate = 20
		self.terminal = terminal

		self.clients = {}
		self.disconnectQueue = []

		self.running = False
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.setblocking(0)

		self.__newID = 0
		self.__lastTime = time.time()
		self.__currentTime = time.time()
		self.__delta = 0

	def start(self):
		self.sock.bind((self.host, self.port))
		self.running = True
		print("[UDP] Started")
		print("[UDP] Tick Rate: {}".format(self.tickRate))
		self.run()

	def connect(self, addr):
		self.__newID += 1
		self.clients[addr] = {}
		self.clients[addr]["id"] = self.__newID
		self.clients[addr]["timeout"] = time.time()
		self.clients[addr]["data"] = None

	def disconnect(self, addr):
		id = self.clients[addr]["id"]
		del self.clients[addr]

	def sendData(self, addr):
		data = ""
		for client in self.clients:
			if self.clients[client]["data"]:
				data += self.clients[client]["data"]
		if data != "":
			self.sock.sendto(data.encode(), addr)

	def run(self):
		self.__currentTime = time.time()
		self.__lastTime = time.time()

		while self.running:
			self.__delta += self.__lastTime - self.__currentTime
			if self.__delta > 1000 / self.tickRate:
				for addr in self.clients:
					if (time.time() - self.clients[addr]["timeout"]) >= self.connectionLossTimeout:
						self.disconnectQueue.append(addr)

				for addr in self.disconnectQueue:
					self.disconnect(addr)
				self.disconnectQueue = []

				readSockets, writeSockets, errorSockets = select.select([self.sock], [], [], 0.0)
				if readSockets:
					try:
						data, addr = self.sock.recvfrom(self.buffersize)

						if not addr in self.clients:
							self.connect(addr)

						self.clients[addr]["data"] = data.decode()
						self.clients[addr]["timeout"] = time.time() 
						self.sendData(addr)
					except socket.error:
						pass

				self.__delta = 0
				self.__currentTime = time.time()
			self.__lastTime = time.time()

if __name__ == "__main__":
	server = ServerUDP()
	server.start()

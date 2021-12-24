import socket
import threading
import select
import sys, time

from constTCP import *

class ServerTCP:
	def __init__(self, terminal):
		self.host = "26.111.238.153"
		self.port = 7171
		self.buffersize = 1024
		self.connectionLossTimeout = 5.0

		self.__newID = 0
		self.running = False
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.clients = {}
		self.terminal = terminal

	def start(self):
		#try:
		self.sock.bind((self.host, self.port))
		self.sock.listen(1)
		self.running = True
		print("[TCP] Started")

		threading.Thread(target=self.mainLoop, args=()).start()
		self.terminal.run()

		#except:
		#	print("Could not start the server with address {}:{}".format(self.host, self.port))
		#	sys.exit(-1)

	def processEvent(self, data, client):
		if ";" in data:
			newData = data.split(";")
			header = int(newData[0])
		else:
			header = int(data)
			
		if client:
			if header == DISCONNECT:
				self.disconnect(client)

			elif header == TIMEOUT:
				self.clients[client]["timeout"] = time.time()

			elif header == GET_ID:
				ret = "{};{}".format(GET_ID, self.clients[client]["id"])
				client.send(ret.encode())

			elif header == DATA:
				for c in self.clients:
					ret = "{};{}".format(self.clients[c]["id"], data)
					c.send(ret.encode())

	def clientHandler(self, client, addr):
		while self.running:
			if (time.time() - self.clients[client]["timeout"]) >= self.connectionLossTimeout:
				break
			try:
				readSockets, writeSockets, errorSockets = select.select([client], [], [], 0.0)

				if readSockets:
					data = client.recv(self.buffersize).decode()
					if data:
						self.processEvent(data, client)
			except:
				pass

		self.disconnect(client)

	def disconnect(self, client):
		id = self.clients[client]["id"]
		data = "0;{}".format(id)
		for c in self.clients:
			try:
				if c != client:
					c.send(data.encode())
			except:
				cid = self.clients[c]["id"]
				print("ERROR -> ID: {}, CID: {}".format(id, cid))
			
		del self.clients[client]
		client.close()
		self.terminal.addMessage("[TCP] Player disconnected from server, id: {}".format(id))

	def connect(self, client, addr):
		self.__newID += 1
		self.clients[client] = {}
		self.clients[client]["id"] = self.__newID
		self.clients[client]["addr"] = addr
		self.clients[client]["timeout"] = time.time()
		self.clients[client]["data"] = None

		threading.Thread(target=self.clientHandler, args=(client, addr), daemon=True).start()
		self.terminal.addMessage("[TCP] New player connected, id: {}".format(self.__newID))

	def mainLoop(self):
		while self.running:
			try:
				client, addr = self.sock.accept()
				if not client in self.clients:
					self.connect(client, addr)
			except:
				pass

	def close(self):
		self.running = False
		self.sock.close()
		print("Server Closed!")
		sys.exit(0)

if __name__ == "__main__":
	server = ServerTCP()
	server.start()
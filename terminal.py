import sys, os

class Terminal:
	def __init__(self):
		self.__server = None
		self.__messages = []

	def setServer(self, server):
		self.__server = server

	def process(self, command):
		if command == "quit" or command == "exit":
			self.__server.close()

		elif command == "clear" or command == "cls":
			if sys.platform == "win32":
				os.system("cls")
			else:
				os.system("clear")

		elif command == "showNextMessage":
			self.showNextMessage()

		elif command == "showAllMessages":
			self.showAllMessages()

		else:
			print("The command '{}' dont exist.".format(command))

	def addMessage(self, msg):
		self.__messages.append(msg)

	def showNextMessage(self):
		if len(self.__messages) > 0:
			print(self.__messages[0])
			self.__messages.pop(0)
		else:
			print("No new messages.")

	def showAllMessages(self):
		if len(self.__messages) > 0:
			for msg in self.__messages:
				print(msg)
			self.__messages = []
		else:
			print("No new messages.")

	def run(self):
		while self.__server.running:
			cmd = input(">> ")
			if cmd != "":
				self.process(cmd)
			if len(self.__messages) > 0:
				print("has {} new messages!".format(len(self.__messages)))
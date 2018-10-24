import socket
import threading
import sys
import time
import os
class Client():
	
	hostdeconnexion=input("entrer le host:")
	portdeconnexion=input("numéro de port:")

	def __init__(self, host=hostdeconnexion, port=portdeconnexion):	
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((str(host), int(port)))
		msg_recv = threading.Thread(target=self.receptiondemessage)
		msg_recv.start()
		
		while True:
			msg = input('')
			if msg=="sf":
				self.envoidefichier()
			elif msg != 'exit':
				self.envoyerunmessage(msg)	
			else:
				self.envoyerunmessage("exit")
				self.sock.close()
				sys.exit()

	def envoidefichier(self):
		try :
			self.sock.send(bytes("partagedefichier","utf8"))    
			nomdefichier=input("Nom de fichier\n")
			self.sock.send(bytes(nomdefichier,"utf8"))
			mon_fichier = open(nomdefichier,"r")
			contenu=mon_fichier.read()                                         
			self.sock.send(bytes(contenu,"utf8"))
			mon_fichier.close()
		except FileNotFoundError:
			time.sleep(1)
			self.sock.send(bytes("FileNotFoundError","utf8"))
			print("le fichier n'existe pas\n")
		                                           
	def receptiondemessage(self):
		while True:
			try:
				data = self.sock.recv(1024).decode("utf8")
				if data=="vous etes banni":
					self.sock.close()
					sys.exit()
				
				if data=="cf":
					mon_fichier=open("copie","w")
					contenu= self.sock.recv(1024).decode("utf8")
					mon_fichier.write(contenu)
					mon_fichier.close()
					print("fin de transfer de fichier")

				elif data !="cf":
					print(data)                                  

			except:
				pass

	def envoyerunmessage(self, msg):
		self.sock.send(bytes(msg, "utf8"))
		
c = Client()
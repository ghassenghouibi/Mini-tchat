import socket
import threading
import sys
import pickle
import os

class Serveur():

	hostdeconnexion=input("entrer le host:")
	portdeconnexion=input("numéro de port:")
	def __init__(self, host=hostdeconnexion, port=portdeconnexion):
		clients = {}
		addresses = {}
		names=[]
		listedavertissement=[]
		#listedavertissement=[]
		self.serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serveur.bind((str(host), int(port)))
		self.serveur.listen(5)
		accepterthread=threading.Thread(target=self.accepterlesconnexions,args=(names,clients,addresses,listedavertissement))
		accepterthread.daemon = True
		accepterthread.start()
		print("Demmarage de ychat v1.0\n")
		while True:
			msg = input('Serveur en attente de connexion\n')
			if msg == 'exit':
				self.serveur.close()
				sys.exit()
			
				


	def accepterlesconnexions(self,names,clients,addresses,listedavertissement):
		
		listedecommande=['lu','historique','clear','prive','sf','fichier','aide','avertir','exit']
		while True:
			client, client_address = self.serveur.accept()
			print("%s:%s vient de se connecter sur le serveur  " % client_address)
			client.send(bytes("Choissisez votre login", "utf8"))
			addresses[client] = client_address
			name = client.recv(1024).decode("utf8")
			while True:
				if name in names:
					client.send(bytes("ce login existe déjà", "utf8"))
					name = client.recv(1024).decode("utf8")
				elif name in listedecommande:
					client.send(bytes("c'est une commande usuelles", "utf8"))
					name = client.recv(1024).decode("utf8")
				else:
					names.append(name)
					listedavertissement.append(0)
					catchthread=threading.Thread(target=self.catch_client, args=(client,name,names,clients,addresses,listedavertissement))
					catchthread.daemon=True
					catchthread.start()
					break


	def catch_client(self,client,name,names,clients,addresses,listedavertissement):

		def message(msg, prefix=""): 
		    for sock in clients: 
		        sock.send(bytes(prefix, "utf8")+msg)
		def listerlesclients(client):
		    client.send(bytes("-----------------------\nlistes des utilisateurs\n-----------------------\n","utf8"))
		    for x in names:
		        client.send(bytes(x+"\n","utf8"))
		    client.send(bytes("-----------------------\n","utf8"))
		def listerlescommandes(client):
		    msg = ('les commandes usuelles sont :\n'
		    '-----------------------------------------------------\n'
		    'lu        :lister les utilisateurs connectées\n'
			'historique:charger l histoirque de la discussion\n'
			'clear     :effacer l histoirque de la discussion\n'
			'prive     :envoyer un message prive a un utilisateur\n'
			'sf        :partager un fichier sur le reseau \n'
			'fichier   :recuperer un fichier qui est deja partager sur le reseau\n'
			'aide      :relister les commandes \n'
			'avertir   :3 avertissement vous serez exclu du tchat \n'
			'exit      :quitter le tchat \n'
		    '-----------------------------------------------------\n')
		    client.send(bytes(msg,"utf8"))


		def envoi(client,nomdefichier):
			try:
				mon_fichier=open(nomdefichier,"r")
				contenu=mon_fichier.read()
				client.send(bytes(contenu,"utf8"))
				mon_fichier.close()
			except FileNotFoundError:
				client.send(bytes("le fichier n'existe pas","utf8"))

		def reception(client,nomdefichier):

			client.send(bytes("Copie de "+nomdefichier+" en cours","utf8"))
			contenu=client.recv(1024).decode("utf8")
			if contenu=="FileNotFoundError":
				client.send(bytes("Annulation de copie de fichier","utf8"))
			else :
				mon_fichier = open(nomdefichier, "w")
				mon_fichier.write(contenu)                                  
				client.send(bytes("fichier bien recu","utf8"))
				mon_fichier.close()
			

		def enregistrementdesdonnes(chaine,prefix):
			mon_fichier = open("historique.txt", "a")
			mon_fichier.write(prefix+":"+str(chaine)+"\n")
			mon_fichier.close()

		def effacerladiscussion():
			mon_fichier = open("historique.txt", "w")
			mon_fichier.write("")
			mon_fichier.close()

		def recuperationhistorique(client):
		    mon_fichier=open("historique.txt","r")
		    chaine=mon_fichier.read()
		    client.send(bytes("-----------------------\n","utf8"))
		    client.send(bytes(chaine,"utf8"))
		    client.send(bytes("-----------------------\n","utf8"))
		    mon_fichier.close()

		def avertissement(client):
			try :
				client.send(bytes("le nom d'utilisateur a avertir", "utf8"))
				clientprive = client.recv(1024).decode("utf8")
				indicedeclient=names.index(clientprive)
				listedavertissement[indicedeclient]+=1
			except ValueError:
				client.send(bytes("le nom n'existe pas ","utf8"))
			for client,name in clients.items():
				if clientprive==name and listedavertissement[indicedeclient]==2:
					client.send(bytes("vous etiez avertir 2 fois la troisème vous êtes banni du tchat\n", "utf8"))
				elif clientprive==name and listedavertissement[indicedeclient]==3:
					client.send(bytes("vous etes banni", "utf8"))
					client.close()
					del clients[client]
					names.remove(clientprive)
					listedavertissement.remove(3)
					message(bytes("%s a etait banni" % clientprive, "utf8"))
					break
			
		def sendtoone(msg,prefix,client):
			for sock in clients:
				if sock==client:
					sock.send(bytes("t'as recu un message","utf8"))

		def lesmessageprives(prefix,client):
		    
		    client.send(bytes("le nom d'utilisateur a envoyer le message svp", "utf8"))
		    clientprive = client.recv(1024).decode("utf8")
		    if clientprive in names:
		    	client.send(bytes("votre message svp","utf8"))
		    	messageprive=client.recv(1024).decode("utf8")
		    	for client, name in clients.items():
    				if name==clientprive:
    					client.send(bytes((prefix+messageprive),"utf8"))	

		    else:
		    	client.send(bytes("l'utilisateur n'exsiste pas","utf8"))

		def sendtoall(msg, prefix,client):
		    for sock in clients:
		        if sock!= client:
		            sock.send(bytes(prefix, "utf8")+msg)

		def deconnexion(client,name):

		    client.send(bytes("exit", "utf8"))
		    client.close()
		    del clients[client]
		    message(bytes("%s a quitter le tchat." % name, "utf8"))
		    names.remove(name)

		welcome = ('Bonjour %s! \nles commandes usuelles sont :\n'
		'-----------------------------------------------------\n'
		'lu        :lister les utilisateurs connectées\n'
		'historique:charger l histoirque de la discussion\n'
		'clear     :effacer l histoirque de la discussion\n'
		'prive     :envoyer un message prive a un utilisateur\n'
		'sf        :partager un fichier sur le reseau \n'
		'fichier   :recuperer un fichier qui est deja partager sur le reseau\n'
		'aide      :relister les commandes \n'
		'avertir   :3 avertissement vous serez exclu du tchat \n'
		'exit      :quitter le tchat \n'
		'-----------------------------------------------------\n'% name)
		msg = "%s viens de se connecter" % name
		
		message(bytes(msg,'utf8'))
		
		clients[client] = name
		client.send(bytes(welcome, "utf8"))
		try :
			while True:
				msg = client.recv(1024)
				if msg==bytes("prive","utf8"):
					lesmessageprives(name+":",client)
				elif msg==bytes("aide","utf8"):
					listerlescommandes(client)
				elif msg ==bytes("lu","utf8"):
					listerlesclients(client)

				elif msg==bytes("avertir","utf8"):
					avertissement(client)
				elif msg==bytes("room","utf8"):
					creationderoom(client)
				elif msg==bytes("historique","utf8"):
					recuperationhistorique(client)
				elif msg ==bytes("clear","utf8"):
					client.send(bytes("l'historique a etait effacer avec succes","utf8"))
					effacerladiscussion()
				elif msg==bytes("partagedefichier","utf8"):
					nomdefichier=client.recv(1024).decode("utf8")
					reception(client,nomdefichier)
					#client.send(bytes("fin de transfer de fichier","utf8"))
				elif msg==bytes("fichier","utf8"):
					client.send(bytes("Nom du fichier","utf8"))
					nomdefichier=client.recv(1024).decode("utf8")
					try :
						fic=open(nomdefichier,"r")
						fic.close()
						client.send(bytes("cf","utf8"))
						envoi(client,nomdefichier)
						#client.send(bytes("fin de transfer de fichier","utf8"))

					except FileNotFoundError:
						client.send(bytes("le fichier n'existe pas","utf8"))

				elif msg != bytes("exit", "utf8"):
					sendtoall(msg, name+": ",client)
					enregistrementdesdonnes((msg).decode("utf8"),name)
				else:
					deconnexion(client,name)
		except OSError:
			pass

s=Serveur()
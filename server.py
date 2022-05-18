#! /usr/bin/python3.10
import os
import sys
import socket
import select
import signal
import atexit

MAXBYTES = 4096

#Creation d'un objet serveur, j'ai trouvé que c'était une bonne idée pour se passer de variable global
class Server:
    #Initialisation du serveur avec host et port
    def __init__(self,host,port) -> None:
        self.serversocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.serversocket.bind((host,port))
        self.serversocket.listen()
        print("Lancement du serveur")
        #Compte le nombre de socket ouvert
        self.nb_open = 0
        #Liste avec les sockets ouverts
        self.socketlist = [self.serversocket]
        #Liste avec les pid des futures sessions
        self.list_pid = []
        #Traitant du signal SIGINT
        signal.signal(signal.SIGINT,self.handler_sigint)

    #Fonction principale du serveur
    def run(self):
        while True:
            (activesocket,_,_) = select.select(self.socketlist,[],[])
            for s in activesocket:
                if s == self.serversocket:
                    clientsocket,(addr,port) = self.serversocket.accept()
                    self.nb_open += 1
                    if addr != "127.0.0.1":
                        clientsocket.close()
                        self.nb_open -= 1
                        break
                    self.socketlist.append(clientsocket)

                    #Condition pour limiter le nombre de connexion
                    if self.nb_open == 4:
                        pidc,status = os.wait()
                        self.list_pid.remove(pidc)
                        self.nb_open -= 1
                        
                    else:
                        #On lance une session
                        print(f"Connexion de {addr} sur le port {port}")
                        pid = os.fork()
                        if pid == 0:
                            self.session(clientsocket,addr,port)
                        else:
                            self.list_pid.append(pid)
                else:
                    #Fermeture du socket
                    self.socketlist.remove(s)
                    self.nb_open -= 1 
                    s.close()
                
                try:
                    #Récupère les fils terminés 
                    pid,status = os.wait(0,os.WNOHANG)
                    #WNOHANG permet de ne pas bloquer le serveur, si aucun fils ne c'est terminé il renvoie 0
                    if pid != 0:
                        self.list_pid.remove(pid)
                except:
                    pass

    #Fonction de session 
    def session(self,s,addr,port):
        #Entrée et sortie standard redirigées
        os.dup2(s.fileno(), 0)
        os.dup2(s.fileno(), 1)
        try:
            #On lance un traitant
            os.execvp(sys.argv[1], [sys.argv[1]])    
        except Exception as e:
            print(e)
            sys.exit(1)

    #Fonction de traitement du signal SIGINT
    def handler_sigint(self,sig,ignore):
        #On SIGINT tout les fils
        for pid in self.list_pid:
            os.kill(pid,signal.SIGINT)
            os.wait()
        self.serversocket.close()
        print("Fermeture du serveur")
        self.delete()
        sys.exit(0)

    #Fonction pour retirer les fichiers produits par le serveur et ses fils
    def delete(self):
        try:
            for f in os.listdir("/tmp/historique"):
                os.unlink(f"/tmp/historique/{f}")
            os.removedirs("/tmp/historique")
        except:
            pass

if __name__ == "__main__":
    #Condition pour lancer le serveur
    if len(sys.argv) != 3  or int(sys.argv[2]) < 2000:
        print("Usage :", sys.argv[0], "traitant port(> 2000)")
        sys.exit(1)
    
    host = "localhost"
    port = int(sys.argv[2])
    #Creation du dossier historique
    try:
        os.mkdir("/tmp/historique")
    except Exception as e:
        print(f"Erreur dans la création du dossier de l'historique : {e}")
    #Lancement du serveur
    server = Server(host, port)
    server.run()
    #On enregistre les fonctions à appeler à la fermeture du programme
    atexit.register(server.handler_sigint,signal.SIGINT)
    atexit.register(server.delete)
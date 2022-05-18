#! /usr/bin/python3.10
import os,sys,time

MAXBYTES = 800000

#Permet de traduire les données reçues
def escaped_utf8_to_utf8(s):
    res = b'' ; i = 0
    while i < len(s):
        if s[i] == '%':
            res += int(s[i+1:i+3], base=16).to_bytes(1, byteorder='big')
            i += 3
        else :
            res += s[i].encode("utf-8")
            i += 1
    return res.decode("utf-8")

#Récupère la réponse html
msg = os.read(0,MAXBYTES)
#Ecrit dans la sortie d'erreur

#os.write(2,msg) # Ecrit la réponse dans la sortie d'erreur

#Prépare la réponse
test = msg.decode("utf-8")
tmp = test.split("\r\n")
#os.write(2,str(tmp[0]).encode("utf-8")) # Ecrit la première ligne de la réponse dans la sortie d'erreur


if "GET" not in tmp[0] or "HTTP/1.1" not in tmp[0]:
    os.write(sys.stderr.fileno(),b"request not supported\n")
    sys.exit(1)
else:
    #On vérifie si le code reçu est vide ou non
    if len(tmp[0]) == 14:
        #Première connection on lui attribue un pid pour sauvegarder ses commandes
        pid = os.getpid()
        #Sert a éviter les bugs, dans mes test le pid à toujours été de 4 chiffres et j'ai pensé trop tard qu'il pouvait être supérieur
        if len(str(pid)) == 3:
            pid *= 10
        if len(str(pid)) > 4:
            pid = int(str(pid)[:4])
    else:
        #On récupère le pid de la connection
        pid = str(tmp[0])[-13:-9]
        

    #On récupère le texte saisis
    saisie = str(tmp[0])[19:-36]
    saisie = escaped_utf8_to_utf8(saisie.replace("+",' '))


    time = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

    #Re ouverture pour écriture
    fp = os.open(f"/tmp/historique/session_{pid}.txt",os.O_WRONLY | os.O_APPEND |os.O_CREAT)
    date = time.encode("utf-8") + b" "
    if saisie != '':
        os.write(fp,date)
    os.write(fp,saisie.encode("utf-8"))
    os.close(fp)

    #Ouverture de la sauvegarde pour lecture du contenue, la crée si elle n'existe pas
    fp = os.open(f"/tmp/historique/session_{pid}.txt",os.O_RDONLY)
    if fp:
        recup = os.read(fp,MAXBYTES)
        #recup = recup.replace(b"\n",b"<br>")
    else:
        recup = b''
    os.close(fp)

    

    recup += b"<br>"
    #os.write(2,recup)

    
    #Création d'un fils qui excécute la commande et l'écrit dans un pipe
    read,write = os.pipe()
    fils = os.fork()
    if fils == 0:
        os.close(read)  
        os.dup2(write,1)
        os.execvp('sh', ['sh','-c', saisie])
    os.wait()
    os.close(write)

    #On récupère le contenue du pipe te le traite
    saisie = os.read(read,MAXBYTES)
    saisie = saisie.replace(b"\n",b"<br>")
    saisie += b"<br>"
    os.write(2,saisie)
    
    recup += saisie
    recup += b'<br>'

    #On ouvre le fichier avec la sauvegarde pour écrire dedans
    fp = os.open(f"/tmp/historique/session_{pid}.txt",os.O_WRONLY | os.O_APPEND)
    os.write(fp,saisie)
    os.close(fp)

    #Mise en forme du code html retour
    header = b"HTTP/1.1 200\nContent-Type: text/html; charset=utf-8\nConnection: close\nContent-Length: 2000\n\n"
    form = (f"""<form action="ajoute" method="GET"><label for='saisie'>{time}</label><input type="text" name="saisie" placeholder="Tapez quelque chose" /><input type="submit" name="send" value="&#9166;"><input name='getpid' type='hidden' value={pid}></form>""").encode("utf-8")
    html = b"<!DOCTYPE html><head><link rel='icon' href='data:;base64,='><title>WebShell</title></head><body>"+ b"<br>"+ recup +form +b"<br>"  +b" </body></html>"
    #E²nvoie de la réponse
    os.write(1,header + html)

sys.exit(0)



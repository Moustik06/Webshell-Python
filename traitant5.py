#! /usr/bin/python3.10
import os,sys

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


#Récupère la trame html
msg = os.read(0,MAXBYTES)
#Ecrit dans la sortie d'erreur
os.write(2,msg)

tmp = msg.decode("utf-8")
tmp = tmp.split("\r\n")

os.write(2,str(tmp[0]).encode("utf-8"))


if "GET" not in tmp[0] or "HTTP/1.1" not in tmp[0]:
    os.write(2,b"request not supported\n")
    sys.exit(1)
else:
    #On vérifie si le code reçu est vide ou non
    if len(tmp[0]) == 14:
        #Première connection on lui attribue un pid pour sauvegarder ses commandes
        pid = os.getpid()
    else:
        #On récupère le pid de la connection
        pid = str(tmp[0])[-13:-9]

    #On récupère le texte saisis
    saisie = str(tmp[0])[19:-36]
    saisie = escaped_utf8_to_utf8(saisie.replace("+",' '))
    saisie += "<br>"

    #Ouverture de la sauvegarde pour lecture du contenue, la crée si elle n'existe pas
    fp = os.open(f"/tmp/historique/session_{pid}.txt",os.O_RDONLY | os.O_CREAT)
    if fp:
        recup = os.read(fp,MAXBYTES)
    else:
        recup = b''
    os.close(fp)
    #Re ouverture pour écriture
    fp = os.open(f"/tmp/historique/session_{pid}.txt",os.O_WRONLY | os.O_APPEND)
    tmp+="<br>"
    os.write(fp,saisie.encode("utf-8"))
    os.close(fp)

    recup += saisie.encode("utf-8")
    #Mise en forme du code html retour
    header = b"HTTP/1.1 200\nContent-Type: text/html; charset=utf-8\nConnection: close\nContent-Length: 2000\n\n"
    form = (f"""<form action="ajoute" method="GET"><input type="text" name="saisie" placeholder="Tapez quelque chose" /><input type="submit" name="send" value="&#9166;"><input name='getpid' type='hidden' value={pid}></form>""").encode("utf-8")
    html = b"<!DOCTYPE html><head><link rel='icon' href='data:;base64,='><title>WebShell</title></head><body>"+ b"<br>"+ recup +form +b"<br>"  +b" </body></html>"
    #Ecriture du code html
    os.write(1,header + html)

sys.exit(0)



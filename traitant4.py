#! /usr/bin/python3.10
import os,sys

def escaped_utf8_to_utf8(s):
    res = b'' ; i = 0
    while i < len(s):
        if s[i] == '%':
            res += int(s[i+1:i+3], base=16).to_bytes(1, byteorder='big')
            i += 3
        else :
            res += s[i].encode("utf-8")
            i += 1
    return res.decode('utf-8')    
    
MAXBYTES = 800000
msg = os.read(0,MAXBYTES)
os.write(2,msg)
#os.write(1,msg)
test = msg.decode("utf-8")
tmp = test.split("\r\n")
#os.write(2,tmp[0].encode("utf-8"))

if "GET" not in tmp[0] or "HTTP/1.1" not in tmp[0]:
    os.write(sys.stderr.fileno(),b"request not supported\n")
    sys.exit(1)
else:
    saisie = str(tmp[0])[19:-24]
    os.write(2,str(saisie).encode("utf-8"))
    os.write(2,b"\n")
    saisie = escaped_utf8_to_utf8(saisie.replace("+",' '))
    saisie += "<br>"
    fp = os.open(f"/tmp/historique/session_.txt",os.O_RDONLY | os.O_CREAT)
    if fp:
        recup = os.read(fp,MAXBYTES)
    else:
        recup = b''
    os.close(fp)

    fp = os.open(f"/tmp/historique/session_.txt",os.O_WRONLY | os.O_APPEND)
    tmp+="<br>"
    os.write(fp,saisie.encode("utf-8"))
    os.close(fp)
    recup += saisie.encode("utf-8")
    #os.write(2,recup)
    header = b"HTTP/1.1 200\nContent-Type: text/html; charset=utf-8\nConnection: close\nContent-Length: 2000\n\n"
    form = b"""<form action="ajoute" method="get"><input type="text" name="saisie" placeholder="Tapez quelque chose" /><input type="submit" name="send" value="&#9166;"></form>"""
    form_pid = b"""<form action="session_{} method="get"></form>"""
    html = b"<!DOCTYPE html><head><link rel='icon' href='data:;base64,='><title>Hello, world!</title></head><body>"+ b"<br>"+ recup +form +b"<br>"  +b" </body></html>"
    os.write(1,header + html)

sys.exit(0)



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

def check(msg):
    i = 1
    tmp = ""
    while msg[i] != '\n':
        tmp+= str(msg[i-1])
        i +=1
    #os.write(2,tmp.encode("utf-8"))
    return msg[i-9:i-1] == "HTTP/1.1" and msg[:3] == "GET"

MAXBYTES = 800000
msg = os.read(0,MAXBYTES)
test = msg.decode("utf-8")

tmp = test.split("=")
tmp = tmp[1].split("&")[0]
tmp = escaped_utf8_to_utf8(tmp.replace("+",' '))

if not check(test):
    os.write(sys.stderr.fileno(),b"request not supported\n")
    sys.exit(1)
else:
    header = b"HTTP/1.1 200\nContent-Type: text/html; charset=utf-8\nConnection: close\nContent-Length: 1000\n\n"
    form = b"""<form action="ajoute" method="get"><input type="text" name="saisie" placeholder="Tapez quelque chose" /><input type="submit" name="send" value="&#9166;"></form>"""
    html = b"<!DOCTYPE html><head><title>Hello, world!</title></head><body>"+msg+ b"<br>"+ b"<br>"+ tmp.encode("utf-8")+form +b"<br>"  +b" </body></html>"
    os.write(1,header + html)

sys.exit(0)



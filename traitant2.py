#! /usr/bin/python3.10
import os,sys

MAXBYTES = 800000
msg = os.read(0,MAXBYTES)
test = msg.decode("utf-8")
if not test.startswith("GET / HTTP/1.1"):
    os.write(sys.stderr.fileno(),b"request not supported\n")
    sys.exit(1)
else:
    header = b"HTTP/1.1 200\nContent-Type: text/html; charset=utf-8\nConnection: close\nContent-Length: 1000\n\n"
    html = b"<!DOCTYPE html><head><title>Hello, world!</title></head><body>Bonjour le monde! <br>Coma va, Nizza?</body></html>"
    html2 = b"<!DOCTYPE html><head><title>Hello, world!</title></head><body>"+ msg + b"</body></html>"
    os.write(1,header+html2)


sys.exit(0)
#! /usr/bin/python3.10
import os,sys
MAXBYTES = 800000
msg = os.read(0,MAXBYTES)
tmp = msg.decode("utf-8")
if not tmp.startswith("GET / HTTP/1.1"):
    os.write(sys.stderr.fileno(),b"request not supported\n")
    os.write(2,tmp.encode("utf-8"))
    sys.exit(1)
else:
    os.write(1,msg)
sys.exit(0)
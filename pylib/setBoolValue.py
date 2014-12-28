#!/usr/bin/env python

import sys
import socket

def processArguments():
    if len(sys.argv) != 4:
        usage()
        sys.exit(1)

def usage ():
    print "Usage: setBoolValue.py nodeid commandclass true|false"

def setBoolValue(nodeid, commandclass, value):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 55556))
    msg = "setBoolValue"
    msg += "," + nodeid
    msg += "," + commandclass
    msg += "," + value
    print "sending msg: " + msg
    s.send(msg)
    reply = s.recv(1024)
    print "received reply: " + reply
    s.close()

def main(*args):
    processArguments()
    setBoolValue(args[1], args[2], args[3])

if __name__ == '__main__':
    sys.exit(main(*sys.argv))

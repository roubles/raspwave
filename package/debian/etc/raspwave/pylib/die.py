#!/usr/bin/env python

import sys
import socket

def processArguments():
    if len(sys.argv) != 1:
        usage()
        sys.exit(1)

def usage ():
    print "Usage: die.py"

def main():
    processArguments()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 55555))
    msg = "die"
    print "sending msg: " + msg
    s.send(msg)
    reply = s.recv(1024)
    print "received reply: " + reply

if __name__ == '__main__':
    main()

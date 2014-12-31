#!/usr/bin/env python

import sys
import socket
import logging
from LoggerUtils import getStdoutLogger

def processArguments():
    if len(sys.argv) != 4:
        usage()
        sys.exit(1)

def usage ():
    print "Usage: setBoolValue.py nodeid commandclass true|false"

def setBoolValue(nodeid, commandclass, value, logger = getStdoutLogger(__name__)):
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('localhost', 55556))
        msg = "setBoolValue"
        msg += "," + nodeid
        msg += "," + commandclass
        msg += "," + value
        logger.info("sending msg: " + msg)
        s.send(msg)
        reply = s.recv(1024)
        logger.info("received reply: " + reply)
    except:
        s.close()

def main(*args):
    processArguments()
    setBoolValue(args[1], args[2], args[3])

if __name__ == '__main__':
    sys.exit(main(*sys.argv))

#!/usr/bin/env python

import sys
import socket
def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print "connecting"
    s.connect(('localhost', 55555))
    msg = "postNotification," + ",".join(sys.argv[1:])
    print "sending msg: " + msg
    s.send(msg)

if __name__ == '__main__':
    main()

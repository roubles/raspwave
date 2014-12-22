#!/usr/bin/env python

from NotificationHandler import postNotification
import sys
import socket

def processArguments():
    if len(sys.argv) != 7:
        usage()
        sys.exit(1)

def usage ():
    print "Usage: postNotification node-id state event value commandclass fullhex"

def main():
    processArguments()
    reply = postNotification(*sys.argv[1:])

if __name__ == '__main__':
    main()

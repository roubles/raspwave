#!/usr/bin/env python
import sys
from NotificationHandler import Notification,getNotification

def processArguments():
    if len(sys.argv) < 3:
        usage()
        sys.exit(1)

def usage ():
    print "Usage: getNotificaion node-id notification-index"


def main():
    processArguments()
    n = getNotification(sys.argv[1], sys.argv[2])
    print str(n)
    sys.exit(0)

if __name__ == '__main__':
    main()

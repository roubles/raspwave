#!/usr/bin/env python

import sys
import socket
from NotificationHandler import sendMsg

def main(*args):
    sendMsg(*args[1:])

if __name__ == '__main__':
    sys.exit(main(*sys.argv))

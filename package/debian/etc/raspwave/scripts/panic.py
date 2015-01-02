#!/usr/bin/env python

import sys
from LoggerUtils import setupSecurityLogger
from SecurityUtils import panic

logger = setupSecurityLogger()

def processArguments():
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

def usage ():
    print "Usage: panic.py panic-reason"

def crux(*args):
    processArguments()
    panic(info = args[1])

if __name__=='__main__':
    sys.exit(crux(*sys.argv))

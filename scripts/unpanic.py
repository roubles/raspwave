#!/usr/bin/env python

import sys
from LoggerUtils import setupSecurityLogger
from SecurityUtils import unpanic

logger = setupSecurityLogger()

def processArguments():
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

def usage ():
    print "Usage: unpanic.py unpanic-reason"

def crux(*args):
    processArguments()
    unpanic(info = args[1])

if __name__=='__main__':
    sys.exit(crux(*sys.argv))

#!/usr/bin/env python

import sys
from SecurityUtils import getCurrentAlarmCode, setAlarmCode
from LoggerUtils import setupSecurityLogger

logger = setupSecurityLogger()

def processArguments():
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

def usage ():
    print "Usage: setcode.py some-alphanumeric-code"

def setCode(alarmCode):
    setAlarmCode(alarmCode)
    logger.info("Alarm code has been updated.")

def crux(*args):
    processArguments()
    alarmCode = sys.argv[1]
    setCode(alarmCode)

if __name__=='__main__':
    sys.exit(crux(*sys.argv))

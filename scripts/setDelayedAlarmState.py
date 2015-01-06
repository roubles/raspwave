#!/usr/bin/env python

import sys
from LoggerUtils import setupSecurityLogger
from SecurityUtils import setDelayedAlarmState
from time import sleep

logger = setupSecurityLogger()

def processArguments():
    if len(sys.argv) < 4:
        usage()
        sys.exit(1)

def usage ():
    print "Usage: setDelayedAlarmState.py alarm-state delay desiredStateAlreadySet"

def crux(*args):
    processArguments()
    alarmState = sys.argv[1]
    delay = int(sys.argv[2])
    desiredStateAlreadySet = bool(sys.argv[3])
    setDelayedAlarmState(alarmState, delay, desiredStateAlreadySet)

if __name__=='__main__':
    sys.exit(crux(*sys.argv))

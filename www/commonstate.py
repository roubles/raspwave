#!/usr/bin/python -u
# @author rouble matta

import os
import sys
sys.path.append('/etc/raspwave/pylib')
from LoggerUtils import setupSecurityLogger
from ConfUtils import getExitDelay

logger = setupSecurityLogger()

def setDesiredState (desiredState):
    exitDelay = getExitDelay(desiredState)
    print 'Content-Type: text/html'
    print # HTTP says you have to have a blank line between headers and content
    logger.info("Setting desired state " + desiredState + " after " + str(exitDelay) + " seconds " )
    os.popen('/usr/local/bin/raspscpt /etc/raspwave/scripts/setDelayedAlarmState.py ' + desiredState + ' ' + str(exitDelay) + "&")
    print 'OK'

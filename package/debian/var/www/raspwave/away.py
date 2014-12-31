#!/usr/bin/python -u
# @author rouble matta

import sys
sys.path.append('/etc/raspwave/pylib')
from SecurityUtils import getCurrentAlarmState,setAway
from LoggerUtils import setupSecurityLogger
from ConfUtils import getAwayExitDelay
import cgi, cgitb
import os
import sys

cgitb.enable()

logger = setupSecurityLogger()

print "Content-type: text/html\n\n"
alarmState = getCurrentAlarmState()
currentAlarmState = getCurrentAlarmState()
if currentAlarmState == 'AWAY':
    print "State is already AWAY. Nothing to do."
    sys.exit(1)

logger.info("Arming to AWAY! Current state is: " + alarmState)
print("Arming to AWAY! Current state is: " + alarmState)

awayExitDelay = getAwayExitDelay()
logger.info("Alarm state will be set to AWAY in " + str(awayExitDelay) + " seconds")
print("Alarm state will be set to AWAY in " + str(awayExitDelay) + " seconds")
sys.stdout.flush()

#status = os.popen('/usr/local/bin/raspscpt /var/www/raspwave/setDelayedAlarmState.py AWAY ' + str(awayExitDelay)).read()
status =os.popen('/usr/local/bin/raspscpt /etc/raspwave/scripts/setDelayedAlarmState.py AWAY ' + str(awayExitDelay)).read()
print status

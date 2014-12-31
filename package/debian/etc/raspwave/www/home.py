#!/usr/bin/env python
# @author rouble matta

import sys
sys.path.append('/etc/raspwave/pylib')
from SecurityUtils import getCurrentAlarmState,setHome
from LoggerUtils import setupSecurityLogger
from ConfUtils import getHomeExitDelay
import cgi, cgitb
import os
import sys

cgitb.enable()

logger = setupSecurityLogger()

print "Content-type: text/html\n\n"
alarmState = getCurrentAlarmState()
alarmState = getCurrentAlarmState()
currentAlarmState = getCurrentAlarmState()
if currentAlarmState == 'HOME':
    print "State is already HOME. Nothing to do."
    sys.exit(1)

logger.info("Arming to HOME! Current state is: " + alarmState)
print("Arming to HOME! Current state is: " + alarmState)

homeExitDelay = getHomeExitDelay()
logger.info("Alarm state will be set to HOME in " + str(homeExitDelay) + " seconds")
print("Alarm state will be set to HOME in " + str(homeExitDelay) + " seconds")
sys.stdout.flush()

#status = os.popen('/usr/local/bin/raspscpt /var/www/raspwave/setDelayedAlarmState.py HOME ' + str(homeExitDelay)).read()
status = os.popen('/usr/local/bin/raspscpt /etc/raspwave/scripts/setDelayedAlarmState.py HOME ' + str(homeExitDelay)).read()
print status

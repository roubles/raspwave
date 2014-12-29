#!/usr/bin/env python
# @author rouble matta

import sys
sys.path.append('/etc/raspwave/pylib')
from SecurityUtils import setAlarmState, getCurrentAlarmState
import cgi, cgitb
cgitb.enable()

logger = setupSecurityLogger()

alarmState = getCurrentAlarmState()
logger.info("Arming! Current state is: " + alarmState)
setAlarmState("ARMED")
alarmState = getCurrentAlarmState()
logger.info("Alarm state has been updated to: " + alarmState)

print "Content-type: text/html\n\n"
print "<html><body> Alarm STATE is " + alarmState + "</body></html>"

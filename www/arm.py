#!/usr/bin/env python
# @author rouble matta

import sys
sys.path.append('/etc/raspwave/pylib')
from SecurityUtils import setAlarmState, getCurrentAlarmState
from LoggerUtils import setupSecurityLogger
import cgi, cgitb
cgitb.enable()

logger = setupSecurityLogger()

specificArmedState = "ARMED"
arguments = cgi.FieldStorage()
if "state" in arguments:
    specificArmedState = arguments["state"].value.upper()

alarmState = getCurrentAlarmState()
logger.info("Arming! Current state is: " + alarmState)

print "Content-type: text/html\n\n"
try:
    setAlarmState(specificArmedState)
    alarmState = getCurrentAlarmState()
    logger.info("Alarm state has been updated to: " + alarmState)
    print "<html><body> Alarm STATE is " + alarmState + " </body></html>"
except:
    print "<html><body> Invalid alarm state: " + specificArmedState + " </body></html>"

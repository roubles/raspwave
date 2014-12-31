#!/usr/bin/env python
# @author rouble matta

import sys
sys.path.append('/etc/raspwave/pylib')
from SecurityUtils import setDisarm,getCurrentAlarmState,getCurrentAlarmCode,unpanic
from LoggerUtils import setupSecurityLogger
import cgi, cgitb
cgitb.enable()

logger = setupSecurityLogger()

print "Content-type: text/html\n\n"
currentAlarmCode = getCurrentAlarmCode()
if currentAlarmCode is not None and currentAlarmCode is not "":
    code = ""
    arguments = cgi.FieldStorage()
    if "code" in arguments:
        code = arguments["code"].value
        if (code != getCurrentAlarmCode()):
            print "Invalid code [" + code + "]. Cannot disarm without code."
            sys.exit(1)
    else:
        print "No code queryparam specified (but code is set). Cannot disarm without code."
        sys.exit(2)
else:
    print "No alarm code set. Disarming without code."

unpanic(info = "Un-panicing due to disarm.")
setDisarm()
alarmState = getCurrentAlarmState()
logger.info("Alarm state has been updated to: " + alarmState)

# Might need to turn off any active alarms here
print "Alarm STATE is [" + alarmState + "]"

#!/usr/bin/env python
# @author rouble matta

import sys
sys.path.append('/etc/raspwave/pylib')
from SecurityUtils import setAlarmState,getCurrentAlarmState,getCurrentAlarmCode,unpanic
from LoggerUtils import setupSecurityLogger
import cgi, cgitb
cgitb.enable()

logger = setupSecurityLogger()

code = ""
arguments = cgi.FieldStorage()
if "code" in arguments:
    code = arguments["code"].value
    if (code != getCurrentAlarmCode()):
        print "Content-type: text/html\n\n"
        print "<html><body> Invalid code " + code + "</body></html>"
        sys.exit(1)
else:
    print "Content-type: text/html\n\n"
    print "<html><body> No code specified</body></html>"
    sys.exit(2)

unpanic()
setAlarmState("DISARMED")
alarmState = getCurrentAlarmState()
logger.info("Alarm state has been updated to: " + alarmState)

# Might need to turn off any active alarms here
print "Content-type: text/html\n\n"
print "<html><body> Alarm STATE is " + alarmState + " </body></html>"

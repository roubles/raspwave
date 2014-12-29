#!/usr/bin/env python
# @author rouble matta

import sys
sys.path.append('/etc/raspwave/pylib')
from SecurityUtils import getCurrentAlarmState
import cgi, cgitb
cgitb.enable()

logger = setupSecurityLogger()

alarmState = getCurrentAlarmState()
logger.info("STATE was queried and retrieved as: " + alarmState)

print "Content-type: text/html\n\n"
print "<html><body> Alarm STATE is " + alarmState + "</body></html>"

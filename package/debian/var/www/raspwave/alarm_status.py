#!/usr/bin/env python
# @author rouble matta

import sys
sys.path.append('/etc/raspwave/pylib')
from SecurityUtils import getCurrentAlarmState,isPanic
from LoggerUtils import setupSecurityLogger
import cgi, cgitb
cgitb.enable()

logger = setupSecurityLogger()

alarmState = getCurrentAlarmState()
alarmPanic = isPanic()
report = ""
report += "Alarm State: " + alarmState + "\n"
report += "Alarm Panic: " + str(alarmPanic) + "\n\n"

print "Content-type: text/html\n\n"
print "<html><body><pre>" + report + "</pre></body></html>"

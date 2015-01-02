#!/usr/bin/env python
# @author rouble matta

import sys
sys.path.append('/etc/raspwave/pylib')
from SecurityUtils import getCurrentAlarmState,isPanic,getLastStateChangeTime,getLastPanicTime,getLastAlertTime
from LoggerUtils import setupSecurityLogger
from NotificationHandler import getNodeReport
from ConfUtils import getNodes
import cgi, cgitb
cgitb.enable()

logger = setupSecurityLogger()

alarmState = getCurrentAlarmState()
alarmPanic = isPanic()
report = ""
report += "Alarm State: " + alarmState + "\n"
report += "Alarm Panic: " + str(alarmPanic) + "\n"
report += "Last Panic time: " + str(getLastPanicTime()) + "\n"
report += "Last Alert time: " + str(getLastAlertTime()) + "\n"
report += "Last State Change time: " + str(getLastStateChangeTime()) + "\n\n"
for node in getNodes():
    report += getNodeReport(node) + "\n"

print "Content-type: text/html\n\n"
print "<html><body><pre>" + report + "</pre></body></html>"

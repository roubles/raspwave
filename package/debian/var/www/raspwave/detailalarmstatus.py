#!/usr/bin/env python
# @author rouble matta

import sys
sys.path.append('/etc/raspwave/pylib')
from SecurityUtils import getCurrentAlarmState,isPanic,getLastStateChangeTime,getLastPanicTime,getLastAlertTime,getPreviousAlarmState,getDesiredAlarmState,getDesiredAlarmStateDelay,getAlertPanicTime,getGuiUpdateTime,isPersistent

from LoggerUtils import setupSecurityLogger
import cgi, cgitb
from controlpanel import getBaseUrl

cgitb.enable()

logger = setupSecurityLogger()

alarmState = getCurrentAlarmState()
alarmPanic = isPanic()
report = ""
report += "Alarm State: " + alarmState + "\n"
report += "Alarm Panic: " + str(alarmPanic) + "\n"
report += "Persistence: " + str(isPersistent()) + "\n"
report += "Last Panic time: " + str(getLastPanicTime()) + "\n"
report += "Last Alert time: " + str(getLastAlertTime()) + "\n"
report += "Last State Change time: " + str(getLastStateChangeTime()) + "\n"
report += "Previous State: " + str(getPreviousAlarmState()) + "\n"
report += "Desired State: " + str(getDesiredAlarmState()) + "\n"
report += "Desired State Delay: " + str(getDesiredAlarmStateDelay()) + "\n"
report += "Alert will become panic at: " + str(getAlertPanicTime()) + "\n"
report += "GUI needs to be updated last at: " + str(getGuiUpdateTime()) + "\n\n"

print 'Content-Type: text/html'
print # HTTP says you have to have a blank line between headers and content
print '<html>'
print '  <head>'
print '    <title> Detail Alarm Status </title>'
print '  </head>' 
print '  <body>'
print '  <h1> Detail Alarm Status </h1>'
print '  <pre id="a">' + report + '</pre>'
print '      <button onClick="window.location=\'' + getBaseUrl() + '/raspwave/controlpanel.py\'" style="font: bold 60px Arial">Back to Control Panel</button><br><br>'
print '  </body>'
print '</html>'

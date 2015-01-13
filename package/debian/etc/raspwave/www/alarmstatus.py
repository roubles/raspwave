#!/usr/bin/python -u
# @author rouble matta

import sys
sys.path.append('/etc/raspwave/pylib')
from SecurityUtils import getCurrentAlarmState,getLastStateChangeTime,getLastStateChangeTimeDelta
from Utils import convert_timedelta_str
from controlpanel import getBaseUrl
import cgi, cgitb

cgitb.enable()
exitdelay = ""
desiredstate = ""
already = ""
arguments = cgi.FieldStorage()
if "exitdelay" in arguments:
    exitdelay = arguments["exitdelay"].value
if "desiredstate" in arguments:
    desiredstate = arguments["desiredstate"].value
if "already" in arguments:
    already = arguments["already"].value

currentAlarmState = getCurrentAlarmState()
print 'Content-Type: text/html'
print # HTTP says you have to have a blank line between headers and content
print '<html>'
print '  <head>'
print '    <title>Current state is ' + currentAlarmState + '</title>'
print '  </head>' 
print '  <body>'
print '  <h1> Current state is ' + currentAlarmState + '</h1>'
if desiredstate != currentAlarmState:
    if exitdelay and desiredstate:
        print '  <h6> Setting state to ' + desiredstate + ' after exit delay of ' + exitdelay + ' seconds</h6>'
print '  <h6> State has been ' + getCurrentAlarmState() + ' for ' + convert_timedelta_str(getLastStateChangeTimeDelta()) + ' since ' + str(getLastStateChangeTime()) + '</h6>'
print '      <button onClick="window.location=\'' + getBaseUrl() + '/raspwave/controlpanel.py\'" style="font: bold 60px Arial">Back to Control Panel</button><br><br>'
print '  </body>'
print '</html>'

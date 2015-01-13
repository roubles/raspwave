#!/usr/bin/env python
# @author rouble matta

import sys
sys.path.append('/etc/raspwave/pylib')
from LoggerUtils import setupSecurityLogger
from NotificationHandler import getNCB,NodeControlBlock,getEarliestNotificationOfCurrentState
from ConfUtils import getNodes,getNodeName
from Utils import getTimeElapsed_HHMMSS
import cgi, cgitb
from controlpanel import getBaseUrl
cgitb.enable()

logger = setupSecurityLogger()

print 'Content-Type: text/html'
print # HTTP says you have to have a blank line between headers and content
print '<html>'
print '  <head>'
print '    <title> Node Report </title>'
print '  </head>' 
print '  <body>'
print '  <h1> Node Report </h1>'
for nodeId in getNodes():
    ncb = getNCB(nodeId)
    notification = getEarliestNotificationOfCurrentState(nodeId)
    nodeName = getNodeName(nodeId)
    print '<h2>' + nodeName + '</h2>'
    if ncb:
        print '<h3>' + nodeName + ' has been ' + ncb.state + ' for ' + getTimeElapsed_HHMMSS(notification.time) + '</h3>' 
        print '<p> Current State: ' + ncb.state + ' since ' + str(notification.time) + '</p>' 
        print '<p> Battery Level: ' + str(ncb.batteryValue) + '</p>' 
print '      <button onClick="window.location=\'' + getBaseUrl() + '/raspwave/controlpanel.py\'" style="font: bold 60px Arial">Back to Control Panel</button><br><br>'
print '  </body>'
print '</html>'

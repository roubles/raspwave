#!/usr/bin/python -u
# @author rouble matta

import os
import sys
sys.path.append('/etc/raspwave/pylib')
from SecurityUtils import getCurrentAlarmState
from LoggerUtils import setupSecurityLogger
from ConfUtils import getExitDelay

logger = setupSecurityLogger()

def printPage (desiredState):
    currentAlarmState = getCurrentAlarmState()
    exitDelay = getExitDelay(desiredState)
    if currentAlarmState == desiredState:
        url = "http://irouble.synology.me:8443/raspwave/currentstate.py?already=true"
    else:
        url = "http://irouble.synology.me:8443/raspwave/currentstate.py?exitdelay=" + str(exitDelay) + "&desiredstate=" + desiredState 
    print 'Content-Type: text/html'
    print 'Location: ' + url
    print # HTTP says you have to have a blank line between headers and content
    print '<html>'
    print '  <head>'
    print '    <meta http-equiv="refresh" content="0;url=' + url + '" />'
    print '    <title>You are going to be redirected</title>'
    print '  </head>' 
    print '  <body>'
    print '    Redirecting... <a href="' + url + '">Click here if you are not redirected</a>'
    print '  </body>'
    os.popen('/usr/local/bin/raspscpt /etc/raspwave/scripts/setDelayedAlarmState.py ' + desiredState + ' ' + str(exitDelay) + "&")
    print '</html>'

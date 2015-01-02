#!/usr/bin/env python
# @author rouble matta

import sys
sys.path.append('/etc/raspwave/pylib')
from SecurityUtils import getCurrentAlarmState,panic,getLastStateChangeTimeDelta,getLastStateChangeTime
from LoggerUtils import setupSecurityLogger
from Utils import convert_timedelta_str
import cgi, cgitb
cgitb.enable()

logger = setupSecurityLogger()

if __name__ == '__main__':
    print 'Content-Type: text/html'
    print # HTTP says you have to have a blank line between headers and content
    print '<html>'
    print '  <head>'
    print '    <title> Panic-ing </title>'
    print '  </head>'
    print '  <body>'
    infoText="Panic-ing from web interface."
    panic(info = infoText)
    print '  <h1> Panic-ing </h1>'
    print '  <h1> Current state is ' + getCurrentAlarmState() + '</h1>'
    print '  <h6> State has been ' + getCurrentAlarmState() + ' for ' + convert_timedelta_str(getLastStateChangeTimeDelta()) + ' since ' + str(getLastStateChangeTime()) + '</h6>'
    print '      <button onClick="window.location=\'http://irouble.synology.me:8443/raspwave/controlpanel.py\'" style="background-color:lightblue;font: bold 60px Arial">Back to Control Panel</button><br><br>'
    print '  </body>'
    print '</html>'

#!/usr/bin/env python
# @author rouble matta

import os
import sys
sys.path.append('/etc/raspwave/pylib')
from SecurityUtils import getCurrentAlarmState,getLastStateChangeTime,getLastStateChangeTimeDelta
from Utils import convert_timedelta_str
from LoggerUtils import setupSecurityLogger
from alarmcode import testCode
import cgi, cgitb
cgitb.enable()

logger = setupSecurityLogger()

if __name__ == '__main__':
    print 'Content-Type: text/html'
    print # HTTP says you have to have a blank line between headers and content
    print '<html>'
    print '  <head>'
    print '    <title>Disarming</title>'
    print '  </head>'
    print '  <body>'
    print '  <h1>'
    (retVal,code) = testCode(cgi.FieldStorage())
    if retVal == 1:
        print "Invalid code [" + code + "]. Cannot disarm without code."
        exit = True
    elif retVal == 2:
        print "No code queryparam specified (but code is set). Cannot disarm without code."
        exit = True
    elif retVal == 0:
        print "No alarm code set. Disarming without code."
    elif retVal == 3:
        print "Disarming..."
    print '  </h1>'

    if retVal == 0 or retVal == 3:
        infoText="unPanic-ing due to disarm."
        os.popen('/usr/local/bin/raspscpt /etc/raspwave/scripts/disarm.py \"' + infoText + '\"&' )
        print '  <h1> Current state is ' + getCurrentAlarmState() + '</h1>'
        print '  <h6> State has been ' + getCurrentAlarmState() + ' for ' + convert_timedelta_str(getLastStateChangeTimeDelta()) + ' since ' + str(getLastStateChangeTime()) + '</h6>'
    print '      <button onClick="window.location=\'http://irouble.synology.me:8443/raspwave/controlpanel.py\'" style="font: bold 60px Arial">Back to Control Panel</button><br><br>'
    print '  </body>'
    print '</html>'

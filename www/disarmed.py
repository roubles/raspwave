#!/usr/bin/env python
# @author rouble matta

import os
import sys
sys.path.append('/etc/raspwave/pylib')
from LoggerUtils import setupSecurityLogger
from alarmcode import testCode
import cgi, cgitb

cgitb.enable()

logger = setupSecurityLogger()

if __name__ == '__main__':
    print 'Content-Type: text/html'
    print # HTTP says you have to have a blank line between headers and content
    (retVal,code) = testCode(cgi.FieldStorage())
    if retVal == 1:
        logger.info("Invalid code [" + code + "]. Cannot disarm without code.")
        print "Invalid code [" + code + "]. Cannot disarm without code."
    elif retVal == 2:
        logger.info("No code queryparam specified (but code is set). Cannot disarm without code.")
        print "No code queryparam specified (but code is set). Cannot disarm without code."
    elif retVal == 0:
        logger.info("No alarm code set. Disarming without code.")
        print "No alarm code set. Disarming without code."
    elif retVal == 3:
        logger.info("Valid code. Disarming...")
        print "Valid code. Disarming..."

    if retVal == 0 or retVal == 3:
        infoText="unPanic-ing due to disarm."
        os.popen('/usr/local/bin/raspscpt /etc/raspwave/scripts/disarm.py \"' + infoText + '\"&' )
    print 'OK'

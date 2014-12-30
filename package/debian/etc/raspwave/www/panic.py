#!/usr/bin/env python
# @author rouble matta

import sys
sys.path.append('/etc/raspwave/pylib')
from SecurityUtils import getCurrentAlarmState,panic
from LoggerUtils import setupSecurityLogger
import cgi, cgitb
cgitb.enable()

logger = setupSecurityLogger()

infoText="Panic-ing from web interface."
logger.info(infoText)
panic(info = infoText)

print "Content-type: text/html\n\n"
print "<html><body> Panic! </body></html>"

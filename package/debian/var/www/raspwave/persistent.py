#!/usr/bin/env python
# @author rouble matta

import os
import sys
sys.path.append('/etc/raspwave/pylib')
from LoggerUtils import setupSecurityLogger
from SecurityUtils import setPersistent
import cgi, cgitb

cgitb.enable()

logger = setupSecurityLogger()

def getValue (arguments):
    if "value" in arguments:
        if (arguments["value"].value.lower() == "true"):
            return True
    return False

if __name__ == '__main__':
    value = getValue(cgi.FieldStorage())
    logger.info("Setting persistent: " + str(value))
    setPersistent(value)
    print 'Content-Type: text/html'
    print # HTTP says you have to have a blank line between headers and content
    print 'OK'

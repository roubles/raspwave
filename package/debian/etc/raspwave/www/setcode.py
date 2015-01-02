#!/usr/bin/env python
# @author rouble matta

import sys
import hashlib
sys.path.append('/etc/raspwave/pylib')
from SecurityUtils import getCurrentAlarmCode,setAlarmCode
from LoggerUtils import setupSecurityLogger
import cgi, cgitb
cgitb.enable()

logger = setupSecurityLogger()

print "Content-type: text/html\n\n"

currentAlarmCode = getCurrentAlarmCode()
if currentAlarmCode is not None and currentAlarmCode is not "":
    existingCode = ""
    arguments = cgi.FieldStorage()
    if "existingcode" in arguments:
            existingCode = arguments["existingcode"].value
            if hashlib.md5(existingCode).hexdigest() != currentAlarmCode:
                print "existingcode does not match with what is set. Cannot update code."
                sys.exit(1)
    else:
        print "No existingcode queryparam specified. Cannot update code."
        sys.exit(1)

code = ""
arguments = cgi.FieldStorage()
if "code" in arguments:
    code = arguments["code"].value
    if code is not None:
        setAlarmCode(code)
        print "Alarm Code is set."
    else:
        print "No code specified. Nothing to set."
else:
    print "No code specified. Nothing to set."

#!/usr/bin/env python
# @author rouble matta

import sys
sys.path.append('/etc/raspwave/pylib')
from RobotUtils import writeStringValue,readStringValue
import cgi, cgitb
cgitb.enable()

code = ""
arguments = cgi.FieldStorage()
if "code" in arguments:
    code = arguments["code"].value
    if (code != readStringValue("ALARM_CODE")):
        print "Content-type: text/html\n\n"
        print "<html><body> Invalid code " + code + "</body></html>"
        sys.exit(1)
else:
    print "Content-type: text/html\n\n"
    print "<html><body> No code specified</body></html>"
    sys.exit(2)

writeStringValue("STATE", "DISARMED")
state = str(readStringValue("STATE"))
print "STATE: " + state
# Might need to turn off any active alarms here

print "Content-type: text/html\n\n"
print "<html><body> Alarm STATE is " + state + "</body></html>"

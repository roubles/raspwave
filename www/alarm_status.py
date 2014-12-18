#!/usr/bin/env python
# @author rouble matta

import sys
sys.path.append('/etc/raspwave/pylib')
from RobotUtils import writeStringValue, readStringValue
import cgi, cgitb
cgitb.enable()

state = str(readStringValue("STATE"))
print "STATE: " + state

print "Content-type: text/html\n\n"
print "<html><body> Alarm STATE is " + state + "</body></html>"

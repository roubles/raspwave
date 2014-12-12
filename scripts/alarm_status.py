#!/usr/bin/env python
# @author rouble matta

from strings import writeStringValue, readStringValue
import cgi, cgitb
cgitb.enable()

state = str(readStringValue("STATE"))
print "STATE: " + state

print "Content-type: text/html\n\n"
print "<html><body> Alarm is " + state + "</body></html>"

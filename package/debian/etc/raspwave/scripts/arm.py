#!/usr/bin/env python
# @author rouble matta

from strings import writeStringValue, readStringValue
import cgi, cgitb
cgitb.enable()

writeStringValue("STATE", "ARMED")
print "STATE: " + str(readStringValue("STATE"))

print "Content-type: text/html\n\n"
print "<html><body>hello scritp</body></html>"

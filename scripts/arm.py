#!/usr/bin/env python
# @author rouble matta

from strings import writeStringValue, readStringValue

writeStringValue("STATE", "ARMED")
print "state: " + str(readStringValue("STATE"))

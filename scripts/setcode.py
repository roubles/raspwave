#!/usr/bin/env python

import sys
from RobotUtils import readStringValue, writeStringValue

code = sys.argv[1]
print "Setting code to: " + code
writeStringValue("ALARM_CODE", code)

#!/usr/bin/python -u
# @author rouble matta

import sys
sys.path.append('/etc/raspwave/pylib')
from SecurityUtils import getCurrentAlarmState,getDesiredAlarmState
import cgi, cgitb

cgitb.enable()

if __name__ == '__main__':
    print 'Content-Type: text/html'
    print ''
    print getCurrentAlarmState() + " " + getDesiredAlarmState()

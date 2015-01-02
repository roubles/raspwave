#!/usr/bin/python -u
# @author rouble matta

import sys
sys.path.append('/etc/raspwave/pylib')
from SecurityUtils import getCurrentAlarmState,setAway
from LoggerUtils import setupSecurityLogger
from ConfUtils import getExitDelay
import cgi, cgitb
import os
from commonstate import printPage

cgitb.enable()

if __name__ == '__main__':
    printPage('RELAXED')

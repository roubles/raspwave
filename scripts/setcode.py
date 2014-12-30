#!/usr/bin/env python

import sys
from SecurityUtils import getCurrentAlarmCode, setAlarmCode
from LoggerUtils import setupSecurityLogger

logger = setupSecurityLogger()

def processArguments():
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

def usage ():
    print "Usage: setcode.py some-alphanumeric-code"

def main():
    processArguments()
    code = sys.argv[1]
    setAlarmCode(code)
    alarmCode = getCurrentAlarmCode()
    logger.info("Alarm code has been updated to: " + alarmCode)

if __name__ == '__main__':
    main()

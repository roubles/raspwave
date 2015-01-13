#!/usr/bin/env python
# @author rouble matta

import sys
from SecurityUtils import getCurrentAlarmState,setAlarmState,getLastStateChangeTimeDelta,isPersistent
from LoggerUtils import setupCronbotLogger

logger = setupCronbotLogger()

def processArguments():
    if len(sys.argv) < 4:
        usage()
        sys.exit(1)

def usage ():
    print "Usage: autostateset.py currentState minimumTimeInCurrentStateInSeconds desiredState [true|false]"

def crux(*args):
    logger.info('AutoStateSet: If Current State has been ' + args[1] + ' for more than ' + args[2] + ' seconds then set state to: ' + args[3])

    processArguments()
    if (len(sys.argv) > 4):
        if (args[4].lower() == 'false'):
            persistent = isPersistent()
            if persistent:
                logger.info("AutoStateSet will not set state since persistent is enabled.")
                return 0

    alarmState = getCurrentAlarmState()
    if (alarmState == args[1]):
        lastStateChangeTimeDelta = getLastStateChangeTimeDelta()
        secondsInCurrentState = lastStateChangeTimeDelta.total_seconds()
        if (secondsInCurrentState > int(args[2])):
            logger.info('AutoStateSet: Current State has been ' + alarmState + ' for ' + str(secondsInCurrentState) + ' seconds. Auto setting state to: ' + args[3])
            setAlarmState(args[3])
        else:
            logger.info("AutoStateSet will not set state since current state has been " + alarmState + ' for only ' + str(secondsInCurrentState) + ' seconds')
    else:
        logger.info("AutoStateSet will not set state since current state is " + alarmState)
    return 0

if __name__=='__main__':
    sys.exit(crux(*sys.argv))

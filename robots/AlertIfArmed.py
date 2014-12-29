#!/usr/bin/env python
# @author rouble matta

import sys
from RobotUtils import sendEmail, robotSleep
from SecurityUtils import getCurrentAlarmState,getAlarmStateDelayForNode
from ConfUtils import getNodeName
from Notification import *
from NotificationHandler import getNotificationFromNodeById
from LoggerUtils import setupRobotLogger

logger = setupRobotLogger()

def AlertIfArmed(nodeId, current, previous):
    name = getNodeName(nodeId)
    alarmState = getCurrentAlarmState()
    alarmStateDelay = getAlarmStateDelayForNode(nodeId, alarmState)
    if alarmStateDelay is None:
        logger.info("Not an armed state: " + alarmState)
    else:
        logger.info("We are in the following armed state: [" + alarmState + "]. Siren will be enabled in " + str(alarmStateDelay) + " seconds")
        robotSleep(alarmStateDelay)
        # Now check is enduser has been able to
        # diarm the alarm
        if (getCurrentAlarmState() != "DISARMED"):
           #Sound Alarm!
           sendEmail(logger, ["rouble@gmail.com"],  "[" + alarmState + "] Sound Alarm!", "");
        else:
           logger.info("Alarm disarmed in time!")

def crux(*args):
    current = getNotificationFromNodeById(args[1], args[2])
    previous = getNotificationFromNodeById(args[1], args[3])
    AlertIfArmed(args[1], current, previous)
    return 0

if __name__=='__main__':
    sys.exit(crux(*sys.argv))

#!/usr/bin/env python
# @author rouble matta

import sys
from RobotUtils import sendEmail, robotSleep
from SecurityUtils import getCurrentAlarmState,getAlarmStateDelayForNode,panic
from ConfUtils import getNodeName
from Notification import *
from NotificationHandler import getNotificationFromNodeById
from LoggerUtils import setupRobotLogger
from SensorUtils import getSensorState

logger = setupRobotLogger()

mailto = ["rouble@gmail.com"]

def AlertIfArmed(nodeId, current, previous):
    name = getNodeName(nodeId)
    alarmState = getCurrentAlarmState()
    if (alarmState != "DISARMED"):
        alarmStateDelay = getAlarmStateDelayForNode(nodeId, alarmState)
        if alarmStateDelay is None:
            logger.info("No delay defined for alarm state: [" + alarmState + "]. Defaulting to 10 seconds.")
            alarmStateDelay = "10"
        logger.info("We are in the following armed state: [" + alarmState + "]. Siren will be enabled in " + str(alarmStateDelay) + " seconds")
        subject = "Sensor tripped in state: " + alarmState + " on " + str(current.time)
        body = "Siren will fire in " + alarmStateDelay + " seconds."
        sendEmail(mailto, subject, body)
        robotSleep(alarmStateDelay)
        # Now check is enduser has been able to disarm the alarm
        if (getCurrentAlarmState() != "DISARMED"):
            panic(nodeId = nodeId, info = "Triggered by " + name + ". " + name + " is currently " + getSensorState(current.value))
        else:
            sendEmail(mailto, "Alarm disarmed in time!", "")
            logger.info("Alarm disarmed in time!")

def crux(*args):
    current = getNotificationFromNodeById(args[1], args[2])
    previous = getNotificationFromNodeById(args[1], args[3])
    AlertIfArmed(args[1], current, previous)
    return 0

if __name__=='__main__':
    sys.exit(crux(*sys.argv))

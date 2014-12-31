#!/usr/bin/env python
# @author rouble matta

import sys
from RobotUtils import sendEmail, robotSleep
from SecurityUtils import getCurrentAlarmState,panic
from ConfUtils import getNodeName,getMailto,isDoorWindowOrMotion,getAlarmStateDelayForNode
from Notification import *
from NotificationHandler import getNotificationFromNodeById
from LoggerUtils import setupRobotLogger
from SensorUtils import getSensorState

logger = setupRobotLogger()

mailto = getMailto()

def AlertIfArmed(nodeId, current, previous):
    name = getNodeName(nodeId)
    alarmState = getCurrentAlarmState()
    if (alarmState != "DISARMED"):
        alarmStateDelay = getAlarmStateDelayForNode(nodeId, alarmState)
        if alarmStateDelay is None:
            logger.info("No delay defined for alarm state: [" + alarmState + "]. Defaulting to 10 seconds.")
            alarmStateDelay = 10
        logger.info("We are in the following armed state: [" + alarmState + "]. Siren will be enabled in " + str(alarmStateDelay) + " seconds")
        subject = "Sensor tripped in state: " + alarmState + " on " + str(current.time)
        body = "Siren will fire in " + str(alarmStateDelay) + " seconds."
        sendEmail(mailto, subject, body)
        robotSleep(alarmStateDelay)
        # Now check is enduser has been able to disarm the alarm
        if (getCurrentAlarmState() != "DISARMED"):
            panic(nodeId = nodeId, info = "Triggered by " + name + ". " + name + " is currently " + getSensorState(current.value) + ".")
        else:
            sendEmail(mailto, "Alarm disarmed in time!", "")
            logger.info("Alarm disarmed in time!")

def crux(*args):
    if not isDoorWindowOrMotion(args[2]):
        return 1

    if args[1] != 'control':
        return 1

    current = getNotificationFromNodeById(args[2], args[3], args[1])
    previous = getNotificationFromNodeById(args[2], args[4], args[1])

    AlertIfArmed(args[2], current, previous)
    return 0

if __name__=='__main__':
    sys.exit(crux(*sys.argv))

#!/usr/bin/env python
# @author rouble matta

import sys
from RobotUtils import sendEmail
from SecurityUtils import getCurrentAlarmState
from ConfUtils import getNodeName,getMailto,isDoorWindowOrMotion
from Notification import *
from NotificationHandler import getNotificationFromNodeById,getNodeReport
from LoggerUtils import setupRobotLogger
from Utils import getTimeElapsed_HHMMSS
from SensorUtils import getSensorState

logger = setupRobotLogger()
mailto = getMailto()

# Always send an email, regardless of armed state
def EmailAlertAlways(nodeId, current, previous):
    name = getNodeName(nodeId)
    alarmState = getCurrentAlarmState()
    subject = "[" + str(alarmState) + "] " + str(name) + " is " + getSensorState(current.value) + " at " + str(current.time)
    body = "Door had been " + getSensorState(previous.value) + " for " + getTimeElapsed_HHMMSS(previous.time) + "\n\n"
    body += "Current: " + str(current) + "\n"
    body += "Previous: " + str(previous) + "\n"
    body += getNodeReport(nodeId)
    sendEmail(mailto, subject, body);

def crux(*args):
    if not isDoorWindowOrMotion(args[2]):
        return 1

    if args[1] != 'control':
        return 1

    current = getNotificationFromNodeById(args[2], args[3], args[1])
    previous = getNotificationFromNodeById(args[2], args[4], args[1])

    EmailAlertAlways(args[2], current, previous)
    return 0

if __name__=='__main__':
    sys.exit(crux(*sys.argv))

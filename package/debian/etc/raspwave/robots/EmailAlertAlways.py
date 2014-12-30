#!/usr/bin/env python
# @author rouble matta

import sys
from RobotUtils import sendEmail
from SecurityUtils import getCurrentAlarmState
from ConfUtils import getNodeName
from Notification import *
from NotificationHandler import getNotificationFromNodeById,getNodeReport
from LoggerUtils import setupRobotLogger
from Utils import getTimeElapsed_HHMMSS
from SensorUtils import getSensorState

logger = setupRobotLogger()
mailto = ["rouble@gmail.com"]

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
    current = getNotificationFromNodeById(args[1], args[2])
    previous = getNotificationFromNodeById(args[1], args[3])
    EmailAlertAlways(args[1], current, previous)
    return 0

if __name__=='__main__':
    sys.exit(crux(*sys.argv))

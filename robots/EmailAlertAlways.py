#!/usr/bin/env python
# @author rouble matta

import sys
from RobotUtils import sendEmail
from SecurityUtils import getCurrentAlarmState
from ConfUtils import getNodeName
from Notification import *
from NotificationHandler import getNotificationFromNodeById
from LoggerUtils import setupRobotLogger

logger = setupRobotLogger()

# Always send an email, regardless of armed state
def EmailAlertAlways(nodeId, current, previous):
    name = getNodeName(nodeId)
    alarmState = getCurrentAlarmState()
    if (current.value == "on"):
        sendEmail(["rouble@gmail.com"],  "[" + str(alarmState) + "] " + str(name) + " is open at " + str(current.time), "hello");
        pass
    elif (current.value == "off") :
        sendEmail(["rouble@gmail.com"], "[" + str(alarmState) + "] " + str(name) + " is closed at " + str(current.time), "hello");
        pass

def crux(*args):
    current = getNotificationFromNodeById(args[1], args[2])
    previous = getNotificationFromNodeById(args[1], args[3])
    EmailAlertAlways(args[1], current, previous)
    return 0

if __name__=='__main__':
    sys.exit(crux(*sys.argv))

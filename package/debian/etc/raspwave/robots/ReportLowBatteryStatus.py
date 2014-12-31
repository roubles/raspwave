#!/usr/bin/env python
# @author rouble matta

import sys
from RobotUtils import sendEmail
from ConfUtils import getNodeName,getMailto
from Notification import *
from NotificationHandler import getNotificationFromNodeById,getNodeReport
from LoggerUtils import setupRobotLogger

logger = setupRobotLogger()
mailto = getMailto()

def ReportLowBatteryStatus(nodeId, current):
    try:
        batteryValue = int(current.value)
    except:
        batteryValue = 0

    if (batteryValue < 30) or (batteryValue == 255) : 
        name = getNodeName(nodeId)
        subject = "Low Battery! " + str(name) + "'s battery level is at " + str(current.value) + "% at " + str(current.time)
        body = "Current: " + str(current) + "\n\n"
        body += getNodeReport(nodeId)
        sendEmail(mailto, subject, body);

def crux(*args):
    if args[1] != 'battery':
        return 1

    current = getNotificationFromNodeById(args[2], args[3], args[1])

    ReportLowBatteryStatus(args[2], current)
    return 0

if __name__=='__main__':
    sys.exit(crux(*sys.argv))

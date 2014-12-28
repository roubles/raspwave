#!/usr/bin/env python
# @author rouble matta

import sys
import logging
from RobotUtils import sendEmail, getNodeName, readStringValue
from NotificationHandler import Notification,getNodeReport

logger = setupRobotLogger()

# Always send an email, regardless of armed state
def EmailAlertAlways(id, state, time):
    name = getNodeName(id)
    alarm_state = getCurrentAlarmState()
    if (state == "open"):
        sendEmail(logger, ["rouble@gmail.com"],  "[" + alarm_state + "] " + name + " is open at " + time, getNodeReport(logger, id));
    elif (state == "close") :
        sendEmail(logger, ["rouble@gmail.com"], "[" + alarm_state + "] " + name + " is closed at " + time, getNodeReport(logger,id));

def main(*args):
    EmailAlertAlways(args[1], args[2], args[7])
    return 0

if __name__=='__main__':
    sys.exit(main(*sys.argv))

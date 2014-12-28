#!/usr/bin/env python
# @author rouble matta

import sys
import logging

from RobotUtils import readStringValue, sendEmail, setupRobotLogger
import EmailAlertAlways

logger = setupRobotLogger()

def AlertIfArmed(*args):
    name = getNodeName(id)
    alarm_state = getCurrentAlarmState()
    alarm_state_delay = getAlarmStateDelayForNode(state)
    if delay is None:
        logger.info("Not an armed state: " + alarm_state)
    else:
        robotsleep(logger, delay)
        # Now check is enduser has been able to
        # diarm the alarm
        if (getCurrentAlarmState() != "DISARMED")
           #Sound Alarm!
           sendEmail(logger, ["rouble@gmail.com"],  "[" + alarm_state + "] Sound Alarm!", "");

def main (*args):
    return AlertIfArmed(*args)

if __name__=='__main__':
    sys.exit(main(*sys.argv))

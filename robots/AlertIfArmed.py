#!/usr/bin/env python
# @author rouble matta

import sys
from RobotUtils import sendEmail
from SecurityUtils import getCurrentAlarmState,panic,setLastAlertTime,getLastAlertTime
from ConfUtils import getNodeName,getMailto,isDoorWindowOrMotion,getAlarmStateDelayForNode
from Notification import *
from NotificationHandler import getNotificationFromNodeById,getLatestNotification
from LoggerUtils import setupRobotLogger
from SensorUtils import getSensorState
from SecurityUtils import getLastAlertTimeDelta,setLastAlertTime
from Utils import convert_timedelta_str
from setBoolValue import setBoolValue
from time import sleep
import threading

logger = setupRobotLogger()

mailto = getMailto()
alertLock = threading.RLock()
ignoreReAlertWithinSeconds=30

def buzz ():
    logger.info("Buzz!")
    setBoolValue("6", "37", "true")
    setBoolValue("6", "37", "false")

def sleepWithBuzz(seconds):
    buzzEverySeconds=60
    elapsedSinceLastBuzzSeconds=0
    secondsInt = int(seconds)
    for i in range(1, secondsInt):
        sleep(1)
        elapsedSinceLastBuzzSeconds += 1
        logger.info("Slept for " + str(i) + " seconds")
        logger.info("Slept for " + str(elapsedSinceLastBuzzSeconds) + " seconds since last buzz")
        if (getCurrentAlarmState() == "DISARMED"):
            logger.info("Alarm disarmed while sleeping")
            break
        if elapsedSinceLastBuzzSeconds == buzzEverySeconds: 
            buzz()
            buzzEverySeconds=30
            elapsedSinceLastBuzzSeconds=0

def AlertIfArmed(nodeId, current, previous):
    with alertLock:
        name = getNodeName(nodeId)
        alarmState = getCurrentAlarmState()
        if (alarmState != "DISARMED"):
            logger.info("Sensor tripped on node " + name + " in alarm state: " + alarmState + " on " + str(current.time))
            timeDelta = getLastAlertTimeDelta()
            if timeDelta.total_seconds() <= ignoreReAlertWithinSeconds:
                logger.info("Last alert was " + convert_timedelta_str(timeDelta) + " ago. Ignoring.")
                return
            setLastAlertTime()
            alarmStateDelay = getAlarmStateDelayForNode(nodeId, alarmState)
            if alarmStateDelay is None:
                logger.info("No delay defined for alarm state: [" + alarmState + "]. Defaulting to 10 seconds.")
                alarmStateDelay = 10
            logger.info("We are in the following armed state: [" + alarmState + "]. Siren will be enabled in " + str(alarmStateDelay) + " seconds")
            subject = "Sensor tripped on node " + name + "in alarm state: " + alarmState + " on " + str(current.time)
            body = "Siren will fire in " + str(alarmStateDelay) + " seconds."
            sendEmail(mailto, subject, body)
            sleepWithBuzz(alarmStateDelay)
            # Now check is enduser has been able to disarm the alarm
            if (getCurrentAlarmState() != "DISARMED"):
                notification = getLatestNotification(nodeId)
                panic(nodeId = nodeId, info = "Triggered by " + name + ". " + name + " is currently " + getSensorState(notification.value) + ".")
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

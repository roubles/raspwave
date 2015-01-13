#!/usr/bin/env python
# @author rouble matta

import sys
from RobotUtils import sendEmail
from SecurityUtils import getCurrentAlarmState,panic,setLastAlertTime,getLastAlertTime
from ConfUtils import getNodeName,getMailto,isDoorWindowOrMotion,getAlarmStateDelayForNode
from Notification import *
from NotificationHandler import getNotificationFromNodeById,getLatestNotification
from SensorUtils import getSensorState
from SecurityUtils import getLastAlertTimeDelta,setLastAlertTime,setAlertPanicTime,resetAlertPanicTime
from Utils import convert_timedelta_str,secondsLeft
from UserSpecific import beep
from setBoolValue import setBoolValue
from time import sleep
import threading
from LoggerUtils import setupRobotLogger

logger = setupRobotLogger()

mailto = getMailto()
alertLock = threading.RLock()
ignoreReAlertWithinSeconds=30

def sleepWithBeep(then):
    while True:
        if (getCurrentAlarmState() == "DISARMED"):
            logger.info("Alarm disarmed while sleeping")
            break

        seconds = secondsLeft(then)
        logger.info("Siren is going to go off in " + str(seconds) + " seconds")
        if seconds < 0:
            break
        elif seconds < 30:
            logger.info("Beeping every second")
            beep()
            sleep(1)
        elif seconds < 60:
            logger.info("Beeping every 2 seconds")
            beep()
            sleep(2)
        elif seconds < 90:
            logger.info("Beeping every 3 seconds")
            beep()
            sleep(3)
        elif seconds < 120:
            logger.info("Beeping every 4 seconds")
            beep()
            sleep(4)
        else: 
            sleep(5)

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
            then = datetime.datetime.now() + datetime.timedelta(seconds=alarmStateDelay)
            setAlertPanicTime(str(then))
            logger.info("We are in the following armed state: [" + alarmState + "]. Siren will be enabled in " + str(alarmStateDelay) + " seconds")
            subject = "[" + alarmState + "] Sensor tripped on node " + name + " on " + str(current.time)
            body = "Siren will fire in " + str(alarmStateDelay) + " seconds at " + str(then)
            sendEmail(mailto, subject, body)
            sleepWithBeep(then)
            # Now check is enduser has been able to disarm the alarm
            if (getCurrentAlarmState() != "DISARMED"):
                notification = getLatestNotification(nodeId)
                panic(nodeId = nodeId, info = "Triggered by " + name + ". " + name + " is currently " + getSensorState(notification.value) + ".")
            else:
                sendEmail(mailto, "Alarm disarmed in time!", "")
                logger.info("Alarm disarmed in time!")
            resetAlertPanicTime()

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

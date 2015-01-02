#!/usr/bin/env python
# @author rouble matta

import ConfigParser
import datetime
from CacheUtils import readStringValue, writeStringValue
from ConfUtils import getConfValue,getMailto,getSirens,getPanicMailto
from LoggerUtils import setupSecurityLogger
from RobotUtils import sendEmail
from NotificationHandler import getNodeReport
from Utils import getNowStr,convert_timedelta_str
from setBoolValue import setBoolValue
from time import sleep
import threading

alarmStateKey = "ALARM_STATE"
alarmCodeKey  = "ALARM_CODE"
alarmPanicKey  = "ALARM_PANIC"
lastPanicTimeKey  = "LAST_PANIC_TIME"
lastAlertTimeKey  = "LAST_ALERT_TIME"
lastStateChangeTimeKey = "LAST_STATECHANGE_TIME"
ignoreRePanicWithinSeconds = 30
logger = setupSecurityLogger()

mailto = getMailto()
panicMailto = getPanicMailto()
panicLock = threading.RLock()
stateLock = threading.RLock()

AlarmState = ["RELAXED", "AWAY", "HOME", "DISARMED"]

def getLastPanicTime():
    return getLastTime(lastPanicTimeKey)

def getLastAlertTime():
    return getLastTime(lastAlertTimeKey)

def getLastStateChangeTime():
    return getLastTime(lastStateChangeTimeKey)

def getLastPanicTimeDelta():
    return getLastTimeDelta(lastPanicTimeKey)

def getLastAlertTimeDelta():
    return getLastTimeDelta(lastAlertTimeKey)

def getLastStateChangeTimeDelta():
    return getLastTimeDelta(lastStateChangeTimeKey)

def setLastPanicTime():
    setLastTime(lastPanicTimeKey)

def setLastAlertTime():
    setLastTime(lastAlertTimeKey)

def setLastStateChangeTime():
    setLastTime(lastStateChangeTimeKey)

def howManySecondsAgoWasLastTime(key):
    return getLastTimeDelta(key).total_seconds()

def getLastTime(key):
    try:
        lastTimeString = readStringValue(key)
        lastTime = datetime.datetime.strptime(lastTimeString, "%Y-%m-%d %H:%M:%S.%f")
    except:
        lastTime = datetime.datetime(1970,1,1)
    return lastTime

def getLastTimeDelta(key):
    lastTime = getLastTime(key)
    return (datetime.datetime.now() - lastTime)

def setLastTime(key):
    now = str(datetime.datetime.now())
    logger.info("Setting key: " + key + ", to " + now)
    writeStringValue(key,now)

def panic (nodeId = None, info = None, siren = True):
    with panicLock:
        logger.info("Panic called.")
        timeDelta = getLastPanicTimeDelta()
        if timeDelta.total_seconds() <= ignoreRePanicWithinSeconds:
            logger.info("Last panic was " + convert_timedelta_str(timeDelta) + " ago. Ignoring.")
            return
        setLastPanicTime()
        writeStringValue(alarmPanicKey, "TRUE")
        # for now, just send an email.
        subject = "Alarm! Alarm! Alarm!"
        body = "Siren sounded at: " + getNowStr() + ".\n"
        if info is not None:
            body += info
            body += "\n\n"
        if nodeId is not None:
            body += getNodeReport(nodeId)  
            body += "\n\n"
        if siren is True:
            soundSirens()
            pass
        logger.info(body)
        sendEmail(mailto, subject, body)
        sendEmail(panicMailto, subject, info)

def soundSirens():
    for siren in getSirens():
        #TODO Verify that they are actually on
        setBoolValue(siren, "37", "true", logger)

def silenceSirens():
    for siren in getSirens():
        #TODO Verify that they are actually off
        setBoolValue(siren, "37", "false", logger)

def unpanic (nodeId = None, info = None):
    with panicLock:
        logger.info("unPanic called.")
        if isPanic():
            writeStringValue(alarmPanicKey, "FALSE")
            # for now, just send an email.
            subject = "Alarm silenced!"
            body = "Alarm silenced at: " + str(datetime.datetime.now()) + ".\n"
            if info is not None:
                body += info
            if nodeId is not None:
                body += getNodeReport(nodeId)  
                body += "\n\n"
            silenceSirens()
            logger.info(body)
            sendEmail(mailto, subject, body)
            sendEmail(panicMailto, subject, info)
        else:
            logger.info("Not panicing. Nothing to do.")

def isPanic():
    try:
        if readStringValue(alarmPanicKey) == "TRUE":
            return True
    except KeyError:
        pass
    return False

def getCurrentAlarmState ():
    try:
        return readStringValue(alarmStateKey)
    except KeyError:
        return "DISARMED"

def getCurrentAlarmCode ():
    try:
        return readStringValue(alarmCodeKey)
    except KeyError:
        return None

def setAway ():
    setAlarmState('AWAY')

def setHome ():
    setAlarmState('HOME')

def setDisarm ():
    setAlarmState('DISARMED')

def setAlarmState(alarmState):
    if alarmState not in AlarmState:
        logger.info("Unknown alarm state: " + alarmState)
        raise Exception("Unknown alarm state: " + alarmState)

    logger.info("Capturing state lock")
    with stateLock:
        currentAlarmState = getCurrentAlarmState()
        timeDelta = getLastStateChangeTimeDelta()
        if alarmState != currentAlarmState:
            logger.info("Setting Alarm state to: " + alarmState)
            writeStringValue(alarmStateKey, alarmState)
            setLastStateChangeTime()
            subject = "Alarm state is: " + alarmState + " at " + getNowStr()
            body = "Previous state was " + currentAlarmState + "."
            sendEmail(mailto, subject, body)
        else:
            if alarmState != 'RELAXED':
                subject = "Alarm state is: " + alarmState
                body = "Alarm state has been " + alarmState + " for " + convert_timedelta_str(timeDelta) + "."
                sendEmail(mailto, subject, body)
            logger.info("We are already in state: " + alarmState + ". Nothing to do.")

def setDelayedAlarmState (alarmState, delay):
    if alarmState not in AlarmState:
        logger.info("Unknown alarm state: " + alarmState)
        raise Exception("Unknown alarm state: " + alarmState)

    currentAlarmState = getCurrentAlarmState()
    timeDelta = getLastStateChangeTimeDelta()
    if alarmState != currentAlarmState:
        while delay:
            logger.info("Setting state: " + alarmState + " after " + str(delay) + " seconds.")
            sleep(1)
            delay -= 1
        setAlarmState(alarmState)
        alarmState = getCurrentAlarmState()
        logger.info("Alarm state has been updated to: " + alarmState)
    else:
        if alarmState != 'RELAXED':
            subject = "Alarm state is: " + alarmState
            body = "Alarm state has been " + alarmState + " for " + convert_timedelta_str(timeDelta) + "."
            sendEmail(mailto, subject, body)
        logger.info("We are already in state: " + alarmState + ". Nothing to do.")

def setAlarmCode(alarmCode):
    logger.info("Setting Alarm code to: " + alarmCode)
    sendEmail(mailto, "Setting Alarm code")
    writeStringValue(alarmCodeKey, alarmCode)

#!/usr/bin/env python
# @author rouble matta

import ConfigParser
import datetime
from CacheUtils import readStringValue, writeStringValue
from ConfUtils import getConfValue,getMailto,getSirens,getPanicMailto
from RobotUtils import sendEmail
from NotificationHandler import getNodeReport
from Utils import getNowStr,convert_timedelta_str,secondsLeftFromString
from UserSpecific import beep,longbeep
from setBoolValue import setBoolValue
from time import sleep
import threading
import hashlib
from LoggerUtils import setupSecurityLogger

logger = setupSecurityLogger()

alarmStateKey = "ALARM_STATE"
alarmDesiredStateKey = "ALARM_DESIRED_STATE"
alarmDesiredStateDelay = "ALARM_DESIRED_STATE_DELAY"
alarmPreviousStateKey = "ALARM_PREVIOUS_STATE"
alarmCodeKey  = "ALARM_CODE"
alarmPanicKey  = "ALARM_PANIC"
statePersistentKey = "STATE_PERSISTENT"
lastPanicTimeKey  = "LAST_PANIC_TIME"
lastAlertTimeKey  = "LAST_ALERT_TIME"
alertPanicTimeKey  = "ALERT_PANIC_TIME"
guiUpdateTimeKey  = "GUI_UPDATE_TIME"
lastStateChangeTimeKey = "LAST_STATECHANGE_TIME"
ignoreRePanicWithinSeconds = 30

mailto = getMailto()
panicMailto = getPanicMailto()
panicLock = threading.RLock()
stateLock = threading.RLock()

AlarmState = ["RELAXED", "AWAY", "HOME", "DISARMED"]

def getLastPanicTime():
    return getLastTime(lastPanicTimeKey)

def getLastAlertTime():
    return getLastTime(lastAlertTimeKey)

def getGuiUpdateTime():
    return getLastTime(guiUpdateTimeKey)

def getAlertPanicTime():
    return getLastTime(alertPanicTimeKey)

def getLastStateChangeTime():
    return getLastTime(lastStateChangeTimeKey)

def getLastPanicTimeDelta():
    return getLastTimeDelta(lastPanicTimeKey)

def getAlertPanicTimeDelta():
    return getLastTimeDelta(alertPanicTimeKey)

def getLastAlertTimeDelta():
    return getLastTimeDelta(lastAlertTimeKey)

def getLastStateChangeTimeDelta():
    return getLastTimeDelta(lastStateChangeTimeKey)

def setLastPanicTime():
    setLastTime(lastPanicTimeKey)

def setGuiUpdateTime():
    setLastTime(guiUpdateTimeKey)

def setLastAlertTime():
    setLastTime(lastAlertTimeKey)

def setAlertPanicTime(alertPanicTime):
    writeStringValue(alertPanicTimeKey,alertPanicTime)
    setGuiUpdateTime() # GUI needs to be updated to reflect that alarm will fire.

def resetAlertPanicTime():
    writeStringValue(alertPanicTimeKey,str(datetime.datetime(1970,1,1)))
    setGuiUpdateTime() # GUI needs to be updated to reflect that alarm will fire.

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
        setPanic(True)
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
            setPanic(False)
            subject = "Unpanic! Alarm silenced!"
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

def setPanic (panic):
    if panic:
        writeStringValue(alarmPanicKey, "TRUE")
    else:
        writeStringValue(alarmPanicKey, "FALSE")
    setGuiUpdateTime()

def isPanic():
    try:
        if readStringValue(alarmPanicKey) == "TRUE":
            return True
    except KeyError:
        pass
    return False

def setPersistent (persistent):
    if persistent:
        writeStringValue(statePersistentKey, "TRUE")
    else:
        writeStringValue(statePersistentKey, "FALSE")
    setGuiUpdateTime()

def isPersistent():
    try:
        if readStringValue(statePersistentKey) == "TRUE":
            return True
    except KeyError:
        pass
    return False

def setPreviousAlarmState (state):
    writeStringValue(alarmPreviousStateKey, state)

def getPreviousAlarmState ():
    try:
        return readStringValue(alarmPreviousStateKey)
    except KeyError:
        return "UNKNOWN"

def setDesiredAlarmState (state):
    writeStringValue(alarmDesiredStateKey, state)
    setGuiUpdateTime()

def getDesiredAlarmState ():
    try:
        return readStringValue(alarmDesiredStateKey)
    except KeyError:
        return "UNKNOWN"

def setDesiredAlarmStateDelay (date):
    writeStringValue(alarmDesiredStateDelay, date)
    setGuiUpdateTime()

def getDesiredAlarmStateDelay ():
    try:
        return readStringValue(alarmDesiredStateDelay)
    except KeyError:
        return "UNKNOWN"

def getDesiredAlarmStateDelayAsTime ():
    desiredAlarmStateDelay = getDesiredAlarmStateDelay()
    try:
        return datetime.datetime.strptime(desiredAlarmStateDelay, "%Y-%m-%d %H:%M:%S.%f")
    except:
        return datetime.datetime(1970,1,1)

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

    setDesiredAlarmState(alarmState)
    setDesiredAlarmStateDelay(str(datetime.datetime.now()))
    logger.info("Capturing state lock")
    with stateLock:
        currentAlarmState = getCurrentAlarmState()
        timeDelta = getLastStateChangeTimeDelta()
        if alarmState != currentAlarmState:
            logger.info("Setting Alarm state to: " + alarmState)
            setPreviousAlarmState(currentAlarmState)
            writeStringValue(alarmStateKey, alarmState)
            setLastStateChangeTime()
            setGuiUpdateTime()
            subject = "Alarm state is: " + alarmState + " at " + getNowStr()
            body = "Previous state was " + currentAlarmState + "."
            longbeep()
            sendEmail(mailto, subject, body)
        else:
            if alarmState != 'RELAXED':
                subject = "Alarm state is: " + alarmState
                body = "Alarm state has been " + alarmState + " for " + convert_timedelta_str(timeDelta) + "."
                sendEmail(mailto, subject, body)
            logger.info("We are already in state: " + alarmState + ". Nothing to do.")

def setDelayedAlarmState (alarmState, delay, desiredStateAlreadySet = False):
    if alarmState not in AlarmState:
        logger.info("Unknown alarm state: " + alarmState)
        raise Exception("Unknown alarm state: " + alarmState)

    if desiredStateAlreadySet == False:
        setDesiredAlarmState(alarmState)
        setDesiredAlarmStateDelay(str(datetime.datetime.now() + datetime.timedelta(seconds=delay)))
    else:
        logger.info("Desired state has already been set.")
    currentAlarmState = getCurrentAlarmState()
    timeDelta = getLastStateChangeTimeDelta()
    if alarmState != currentAlarmState:
        desiredAlarmStateDelay = getDesiredAlarmStateDelay() 
        while True: 
            secondsLeft = secondsLeftFromString(desiredAlarmStateDelay)
            if secondsLeft < 0:
                break
            logger.info("Setting state: " + alarmState + " after " + str(secondsLeft) + " seconds.")
            sleep(1)
        currentDesiredAlarmState = getDesiredAlarmState()
        if (currentDesiredAlarmState != alarmState):
            logger.info("Not setting State!!. The current desired state is: " + currentDesiredAlarmState + " and we were waiting to set it to " + alarmState)
            return
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
    logger.info("Setting Alarm code...")
    sendEmail(mailto, "Setting Alarm code")
    md5Alarmcode = hashlib.md5(alarmCode).hexdigest()
    writeStringValue(alarmCodeKey, md5Alarmcode)

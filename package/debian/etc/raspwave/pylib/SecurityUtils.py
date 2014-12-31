#!/usr/bin/env python
# @author rouble matta

import ConfigParser
import datetime
from CacheUtils import readStringValue, writeStringValue
from ConfUtils import getConfValue,getMailto,getSirens,getPanicMailto,getAwayExitDelay,getHomeExitDelay
from LoggerUtils import setupSecurityLogger
from RobotUtils import sendEmail
from NotificationHandler import getNodeReport
from Utils import getNowStr
from setBoolValue import setBoolValue
from time import sleep
import threading

alarmStateKey = "ALARM_STATE"
alarmCodeKey  = "ALARM_CODE"
alarmPanicKey  = "ALARM_PANIC"

logger = setupSecurityLogger()

mailto = getMailto()
panicMailto = getPanicMailto()

AlarmState = ["AWAY", "HOME", "DISARMED"]

def panic (nodeId = None, info = None, siren = True):
    logger.info("Panic called.")
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
        #soundSirens()
        pass
    logger.info(body)
    sendEmail(mailto, subject, body)
    sendEmail(panicMailto, subject, info)

def soundSirens(nodeId):
    for siren in getSirens():
        #TODO Verify that they are actually on
        setBoolValue(siren, "37", "true", logger)

def silenceSirens():
    for siren in getSirens():
        #TODO Verify that they are actually off
        setBoolValue(siren, "37", "false", logger)

def unpanic (nodeId = None, info = None):
    logger.info("unPanic called.")
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

    currentAlarmState = getCurrentAlarmState()
    if alarmState != currentAlarmState:
        logger.info("Setting Alarm state to: " + alarmState)
        subject = "Setting Alarm state to: " + alarmState + " at " + getNowStr()
        body = "Previous state was " + currentAlarmState + "."
        sendEmail(mailto, subject, body)
        writeStringValue(alarmStateKey, alarmState)
    else:
        logger.info("We are already in state: " + alarmState + ". Nothing to do.")

def setDelayedAlarmState (alarmState, delay):
    if alarmState not in AlarmState:
        logger.info("Unknown alarm state: " + alarmState)
        raise Exception("Unknown alarm state: " + alarmState)

    currentAlarmState = getCurrentAlarmState()
    if alarmState != currentAlarmState:
        while delay:
            logger.info("Setting state: " + alarmState + " after " + str(delay) + " seconds.")
            sleep(1)
            delay -= 1
        setAlarmState(alarmState)
        alarmState = getCurrentAlarmState()
        logger.info("Alarm state has been updated to: " + alarmState)
    else:
        logger.info("We are already in state: " + alarmState + ". Nothing to do.")

def setAlarmCode(alarmCode):
    logger.info("Setting Alarm code to: " + alarmCode)
    sendEmail(mailto, "Setting Alarm code")
    writeStringValue(alarmCodeKey, alarmCode)

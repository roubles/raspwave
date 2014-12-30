#!/usr/bin/env python
# @author rouble matta

import ConfigParser
import datetime
from CacheUtils import readStringValue, writeStringValue
from ConfUtils import getConfValue
from LoggerUtils import setupSecurityLogger
from RobotUtils import sendEmail
from NotificationHandler import getNodeReport
from Utils import getNowStr

alarmStateKey = "ALARM_STATE"
alarmCodeKey  = "ALARM_CODE"

logger = setupSecurityLogger()

mailto = ["rouble@gmail.com"]
AlarmState = ["ARMED", "NOMOTION", "NOWAIT", "NOMOTIONNOWAIT", "DISARMED"]

def panic (nodeId = None, info = None, siren = True):
    logger.info("Panic called.")
    # for now, just send an email.
    subject = "Alarm! Alarm! Alarm!"
    body = "Siren sounded at: " + getNowStr() + "\n"
    if info is not None:
        body += info
        body += "\n\n"
    if nodeId is not None:
        body += getNodeReport(nodeId)  
        body += "\n\n"
    if siren is True:
        #TODO Sound siren here. pass for now.
        pass
    logger.info(body)
    sendEmail(mailto, subject, body)

def unpanic (nodeId = None, info = None):
    logger.info("unPanic called.")
    # for now, just send an email.
    subject = "Alarm silenced!"
    body = "Alarm silenced at: " + str(datetime.datetime.now()) + "\n"
    if info is not None:
        body += info
    if nodeId is not None:
        body += getNodeReport(nodeId)  
        body += "\n\n"
    #TODO Switch off siren here.
    logger.info(body)
    sendEmail(mailto, subject, body)

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

def setAlarmState(alarmState):
    if alarmState not in AlarmState:
        raise Exception("Unknown alarm state: " + alarmState)
    logger.info("Setting Alarm state to: " + alarmState)
    sendEmail(mailto, "Setting Alarm state to: " + alarmState)
    writeStringValue(alarmStateKey, alarmState)

def setAlarmCode(alarmCode):
    logger.info("Setting Alarm code to: " + alarmCode)
    sendEmail(mailto, "Setting Alarm code")
    writeStringValue(alarmCodeKey, alarmCode)

def getCurrentAlarmStateDelayForNode(id):
    return getAlarmStateDelayForNode(id, getCurrentState())

def getAlarmStateDelayForNode (id, alarmState):
    try:
        return getConfValue(id, alarmState + "_DELAY") 
    except ConfigParser.NoOptionError:
        return None

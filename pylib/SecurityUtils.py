#!/usr/bin/env python
# @author rouble matta

import ConfigParser
from CacheUtils import readStringValue, writeStringValue
from ConfUtils import getConfValue

alarmStateKey = "ALARM_STATE"
alarmCodeKey  = "ALARM_CODE"

logger = setupSecurityLogger()

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
    logger.info("Setting Alarm state to: " + alarmState)
    writeStringValue(alarmStateKey, alarmState)

def setAlarmCode(alarmCode):
    logger.info("Setting Alarm code to: " + alarmCode)
    writeStringValue(alarmCodeKey, alarmCode)

def getCurrentAlarmStateDelayForNode(id):
    return getAlarmStateDelayForNode(id, getCurrentState())

def getAlarmStateDelayForNode (id, alarmState):
    try:
        return getConfValue(id, alarmState + "_DELAY") 
    except ConfigParser.NoOptionError:
        return None

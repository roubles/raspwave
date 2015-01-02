#!/usr/bin/env python
# @author rouble matta

import ConfigParser
from Utils import get_absolute_path
from EnvUtils import isTestEnvironment

if isTestEnvironment():
    confFile = "~/raspwave/conf/nodes.conf"
else:
    confFile = "/etc/raspwave/conf/nodes.conf"

settingsSection = "SETTINGS"
homeSection = "HOME"
awaySection = "AWAY"

mailtoKey = "MAILTO"
panicMailtoKey = "PANIC_MAILTO"
nodeNameKey = "NAME"
doorWindowKey = "DOORWINDOW"
sirenKey = "SIREN"
motionKey = "MOTION"
exitDelayKey = "EXITDELAY"

def getConfig():
    config = ConfigParser.ConfigParser()
    myConfFile = get_absolute_path(confFile)
    config.read(myConfFile)
    return config

def getConfValue(section, key):
    config = getConfig()
    return config.get(section, key) 

def getMailto ():
    config = getConfig()
    value = config.get(settingsSection, mailtoKey)
    return [x.strip() for x in value.split(',')]

def getPanicMailto ():
    config = getConfig()
    value = config.get(settingsSection, panicMailtoKey)
    return [x.strip() for x in value.split(',')]

def getSirens ():
    config = getConfig()
    value = config.get(settingsSection, sirenKey)
    return [x.strip() for x in value.split(',')]

def getDoorWindows ():
    config = getConfig()
    value = config.get(settingsSection, doorWindowKey)
    return [x.strip() for x in value.split(',')]

def getMotions ():
    config = getConfig()
    value = config.get(settingsSection, motionKey)
    return [x.strip() for x in value.split(',')]

def getNodes ():
    config = getConfig()
    sections = config.sections()
    sections.remove(settingsSection)
    return sections

def getNodeName (id):
    try:
        return getConfValue(id, nodeNameKey)
    except:
        return "Node" + str(id)

def isDoorWindowOrMotion (id):
    if isDoorWindow(id):
        return True
    if isMotion(id):
        return True

def isDoorWindow (id):
    return (id in getDoorWindows())

def isSiren (id):
    return (id in getSirens())

def isMotion (id):
    return (id in getMotions())

def getAlarmStateDelayForNode (id, alarmState):
    try:
        return int(getConfValue(id, alarmState + "_ENTERDELAY"))
    except:
        if alarmState == 'AWAY':
            return 45
        if alarmState == 'RELAXED':
            return 180
        if alarmState == 'HOME':
            return 0
        return 60

def getExitDelay (alarmState):
    try:
        return int(getConfValue(alarmState, exitDelayKey))
    except:
        if alarmState == 'AWAY':
            return 45
        if alarmState == 'RELAXED':
            return 180
        if alarmState == 'HOME':
            return 0
        return 60

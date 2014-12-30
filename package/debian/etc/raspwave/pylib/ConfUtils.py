#!/usr/bin/env python
# @author rouble matta

import ConfigParser
from Utils import get_absolute_path
from EnvUtils import isTestEnvironment

if isTestEnvironment():
    confFile = "~/raspwave/conf/nodes.conf"
else:
    confFile = "/etc/raspwave/conf/nodes.conf"

settingsSection = "settings"
mailtoKey = "MAILTO"
nodeNameKey = "NAME"
doorWindowKey = "DOORWINDOW"
sirenKey = "SIREN"
motionKey = "MOTION"

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
    mailto = config.get(settingsSection, mailtoKey)
    return [x.strip() for x in mailto.split(',')]

def getNodes ():
    config = getConfig()
    sections = config.sections()
    sections.remove(settingsSection)
    return sections

def getNodeName (id):
    try:
        return getConfValue(id, nodeNameKey)
    except:
        return "NONAME"

def isKeyValueTrue (id, key):
    try:
        if getConfValue(id, key).lower() == 'true':
            return True
    except:
        pass
    return False

def isDoorWindowOrMotion (id):
    if isDoorWindow(id):
        return True
    if isMotion(id):
        return True
    return False

def isDoorWindow (id):
    return isKeyValueTrue(id, doorWindowKey)

def isSiren (id):
    return isKeyValueTrue(id, sirenKey)

def isMotion (id):
    return isKeyValueTrue(id, motionKey)

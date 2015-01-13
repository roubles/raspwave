#!/usr/bin/env python
# @author rouble matta

import socket
import ConfigParser
from Utils import get_absolute_path
from EnvUtils import isTestEnvironment
from LoggerUtils import setupNotificationHandlerLogger
from CacheUtils import readStringValue,writeStringValue

logger = setupNotificationHandlerLogger()

if isTestEnvironment():
    confFile = "~/raspwave/conf/nodes.conf"
else:
    confFile = "/etc/raspwave/conf/nodes.conf"

settingsSection = "SETTINGS"
httpUsernameKey = "HTTPUSERNAME"
httpPasswordKey = "HTTPPASSWORD"
httpOrHttpsKey = "HTTPORHTTPS"
hostnameOrIPKey = "HOSTNAME_OR_IP"
localIpKey = "LOCAL_IP" # This is used in the cache, and not from the config per se
httpPortKey = "HTTPPORT"
userId = "USERID"
homeSection = "HOME"
awaySection = "AWAY"
relaxedSection = "RELAXED"
disarmedSection = "DISARMED"

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

def getHttpUsername ():
    return getConfValue(settingsSection, httpUsernameKey)

def getHttpPassword ():
    return getConfValue(settingsSection, httpPasswordKey)

def getHttpOrHttps ():
    try:
        protocol = getConfValue(settingsSection, httpOrHttpsKey)
        if protocol is not None:
            return protocol
    except:
        pass
    return "http"

def getHostnameOrIp ():
    try:
        host = getConfValue(settingsSection, hostnameOrIPKey)
        if host is not None:
            return host
    except:
        pass
    return getLocalIp()

def getLocalIp ():
    try:
        ip = readStringValue(localIpKey)
    except:
        ip = "127.0.0.1"
    return ip

def setLocalIp ():
    # This is a relatively expensive call.
    # http://stackoverflow.com/a/1267524/215120
    try:
        ip = [(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
    except:
        ip = "127.0.0.1"
    logger.info("Setting Local IP to: " + ip)
    writeStringValue(localIpKey, ip)

def getHttpPort ():
    try:
        port = getConfValue(settingsSection, httpPortKey)
        if port is not None:
            return port
    except:
        pass
    return "80"

def getUserId ():
    try:
        return getConfValue(settingsSection, userId)
    except:
        return None

def getMailto ():
    try:
        value = getConfValue(settingsSection, mailtoKey)
        return [x.strip() for x in value.split(',')]
    except:
        return []

def getPanicMailto ():
    try:
        value = getConfValue(settingsSection, panicMailtoKey)
        return [x.strip() for x in value.split(',')]
    except:
        return []

def getSirens ():
    try:
        value = getConfValue(settingsSection, sirenKey)
        return [x.strip() for x in value.split(',')]
    except:
        return []

def getDoorWindows ():
    try:
        value = getConfValue(settingsSection, doorWindowKey)
        return [x.strip() for x in value.split(',')]
    except:
        return []

def getMotions ():
    try:
        value = getConfValue(settingsSection, motionKey)
        return [x.strip() for x in value.split(',')]
    except:
        return []

def getNodes ():
    config = getConfig()
    sections = config.sections()
    try:
        sections.remove(settingsSection)
        sections.remove(homeSection)
        sections.remove(awaySection)
        sections.remove(relaxedSection)
        sections.remove(disarmedSection)
    except:
        pass
    return sections

def getNodeName (id):
    try:
        return getConfValue(id, nodeNameKey)
    except:
        return "Node" + str(id)

def isNode (id):
    if isDoorWindow(id):
        return True
    if isMotion(id):
        return True
    if isSiren(id):
        return True
    return False

def isDoorWindowOrMotion (id):
    if isDoorWindow(id):
        return True
    if isMotion(id):
        return True
    return False

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
            return 90
        if alarmState == 'RELAXED':
            return 180
        if alarmState == 'HOME':
            return 0
        return 90

def getExitDelay (alarmState):
    try:
        return int(getConfValue(alarmState, exitDelayKey))
    except:
        if alarmState == 'AWAY':
            return 90
        if alarmState == 'RELAXED':
            return 180
        if alarmState == 'HOME':
            return 0
        return 90

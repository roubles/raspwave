#!/usr/bin/env python
# @author rouble matta

import ConfigParser
from Utils import get_absolute_path
from EnvUtils import isTestEnvironment

if isTestEnvironment():
    confFile = "~/raspwave/conf/nodes.conf"
else:
    confFile = "/etc/raspwave/conf/nodes.conf"

nodeNameKey = "NAME"

def getConfig():
    config = ConfigParser.ConfigParser()
    myConfFile = get_absolute_path(confFile)
    config.read(myConfFile)
    return config

def getConfValue(section, key):
    config = getConfig()
    return config.get(section, key) 

def getNodes ():
    config = getConfig()
    return config.sections()

def getNodeName (id):
    return getConfValue(id, nodeNameKey)

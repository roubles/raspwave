#!/usr/bin/env python
# @author rouble matta

import anydbm
from Utils import get_absolute_path
from EnvUtils import isTestEnvironment

if isTestEnvironment:
    stringsCacheFile = "~/raspwave/db/strings.cache.db"
else:
    stringsCacheFile = "/etc/raspwave/db/strings.cache.db"

def readStringValue (key):
    strings = anydbm.open(get_absolute_path(stringsCacheFile), 'c')
    value = strings[key]
    strings.close()
    return value

def writeStringValue (key, value):
    strings = anydbm.open(get_absolute_path(stringsCacheFile), 'c')
    strings[key] = value
    strings.close()

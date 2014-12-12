#!/usr/bin/env python
# @author rouble matta

import anydbm

def readStringValue (key):
    strings = anydbm.open("/home/pi/raspwave/db/strings.cache.db", 'c')
    value = strings[key]
    strings.close()
    return value

def writeStringValue (key, value):
    strings = anydbm.open("/home/pi/raspwave/db/strings.cache.db", 'c')
    strings[key] = value
    strings.close()

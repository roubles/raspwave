#!/usr/bin/env python
# @author rouble matta

def getSirenState(value):
    valueStr = str(value)
    if valueStr == "True":
        return "On"
    if valueStr == "False":
        return "Off"
    return "Unknown!"

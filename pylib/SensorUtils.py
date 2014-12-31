#!/usr/bin/env python
# @author rouble matta

def getSensorState(value):
    valueStr = str(value)
    if valueStr == "True":
        return "Open"
    if valueStr == "False":
        return "Closed"
    if valueStr == "0":
        return "Closed"
    if valueStr == "255":
        return "Open"
    return "Unknown!"

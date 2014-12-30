#!/usr/bin/env python
# @author rouble matta

import datetime
import time

class Notification:
    birthMark = 0
    def __init__ (self, nodeId, commandClass, fullHex):
        self.birthMark = Notification.birthMark
        Notification.birthMark += 1
        self.time = datetime.datetime.now()
        self.nid = self.time.strftime("%Y%m%d%H%M%S") + str(self.birthMark)
        self.type = "Notification"
        self.nodeId = nodeId
        self.commandClass = commandClass
        self.fullHex = fullHex
        self.ignore = False
        self.value = None

    def __str__ (self):
        return self.type + " nid[" + str(self.nid) + "], nodeId=[" + str(self.nodeId) + "], commandClass=[" + str(self.commandClass) + "], fullHex=[" + str(self.fullHex) + "], time=[" + str(self.time) + "], ignore=[" + str(self.ignore) + "]"

class ValueNotification(Notification):
    def __init__ (self, nodeId, commandClass, fullHex, value):
        Notification.__init__(self, nodeId, commandClass, fullHex)
        self.value = value
        self.previousValue = None
        self.type = "ValueNotification"

    def __str__ (self):
        return self.type + " nid[" + str(self.nid) + "], nodeId=[" + str(self.nodeId) + "], value=[" + str(self.value) + "], commandClass=[" + str(self.commandClass) + "], fullHex=[" + str(self.fullHex) + "], time=[" + str(self.time) + "], ignore=[" + str(self.ignore) + "]"

class BatteryValueNotification(Notification):
    def __init__ (self, nodeId, commandClass, fullHex, value):
        Notification.__init__(self, nodeId, commandClass, fullHex)
        self.value = value
        self.type = "BatteryValueNotification"

    def __str__ (self):
        return self.type + " nid[" + str(self.nid) + "], nodeId=[" + str(self.nodeId) + "], value=[" + str(self.value) + "], commandClass=[" + str(self.commandClass) + "], fullHex=[" + str(self.fullHex) + "], time=[" + str(self.time) + "], ignore=[" + str(self.ignore) + "]"

class WakeupNotification(Notification):
    def __init__ (self, nodeId, commandClass, fullHex, value):
        Notification.__init__(self, nodeId, commandClass, fullHex)
        self.value = value
        self.type = "WakeupNotification"

    def __str__ (self):
        return self.type + " nid[" + str(self.nid) + "], nodeId=[" + str(self.nodeId) + "], value=[" + str(self.value) + "], commandClass=[" + str(self.commandClass) + "], fullHex=[" + str(self.fullHex) + "], time=[" + str(self.time) + "], ignore=[" + str(self.ignore) + "]"

class NodeEventNotification(ValueNotification):
    def __init__ (self, nodeId, commandClass, fullHex, event):
        Notification.__init__(self, nodeId, commandClass, fullHex)
        self.event = event
        if event is '0':
            self.value = "False"
        elif event == '255':
            self.value = "True"
        else:
            self.value = "unknown"
        self.previousValue = None
        self.type = "NodeEventNotification"

    def __str__ (self):
        return self.type + " nid[" + str(self.nid) + "], nodeId=[" + str(self.nodeId) + "], event=[" + str(self.event) + "], value=[" + str(self.value) + "] commandClass=[" + str(self.commandClass) + "], fullHex=[" + str(self.fullHex) + "], time=[" + str(self.time) + "], ignore=[" + str(self.ignore) + "]"

class ValueChangeNotification(ValueNotification):
    def __init__ (self, nodeId, commandClass, fullHex, value, previousValue):
        Notification.__init__(self, nodeId, commandClass, fullHex)
        self.value = value
        self.previousValue = previousValue
        self.type = "ValueChangeNotification"

    def __str__ (self):
        return self.type + " nid[" + str(self.nid) + "], nodeId=[" + str(self.nodeId) + "], value=[" + str(self.value) + "], previousValue=[" + str(self.previousValue) + "] commandClass=[" + str(self.commandClass) + "], fullHex=[" + str(self.fullHex) + "], time=[" + str(self.time) + "], ignore=[" + str(self.ignore) + "]"

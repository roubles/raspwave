#!/usr/bin/env python
# @author rouble matta

import os
import sys
import shelve
import datetime
import socket
import time
from time import sleep
import logging
import threading
import pickle
import subprocess
from LoggerUtils import setupNotificationHandlerLogger, getNotificationHandlerLogger
from Notification import Notification, ValueNotification, BatteryValueNotification, NodeEventNotification, ValueChangeNotification
from Utils import get_absolute_path
from EnvUtils import isTestEnvironment

logger = None

usrHomeFolder = '~/.raspwave/robots'
if isTestEnvironment():
    raspscptLocation = '~/raspwave/sh/raspscpt'
    etcFolder = '~/raspwave/robots'
    shelfLocation = '~/raspwave/db/nh.shelf'
else:
    raspscptLocation = '/usr/local/bin/raspscpt'
    etcFolder = '/etc/raspwave/robots'
    shelfLocation = '/etc/raspwave/db/nh.shelf'

class NodeControlBlock:
    def __init__(self, nid):
        self.nid = nid
        self.batteryValue = None
        self.lastWakeupTime = None
        self.notifications = []

class RobotLauncher(threading.Thread):
    def __init__ (self, current, previous):
        super(RobotLauncher, self).__init__()
        self.current = current
        self.previous = previous
    def launchRobots(self, folder, current, previous):
        logger.info("Launching all robots in folder: " + folder)
        folder = get_absolute_path(folder)
        if os.path.isdir(folder):
            for filename in os.listdir(folder):
                if filename.endswith(".py"):
                    raspscpt = get_absolute_path(raspscptLocation)
                    cmd = raspscpt + " " + folder + '/' + filename + " " + current.nodeId + " " + current.nid + " " + (previous.nid if previous else "")
                    logger.info(cmd)
                    subprocess.Popen(cmd, shell=True)
        else:
            logger.info("Folder does not exist: " + folder)

    def launchEtcRobots(self, current, previous):
        self.launchRobots(etcFolder, current, previous)
    def launchUsrHomeRobots(self, current, previous):
        self.launchRobots(usrHomeFolder, current, previous)
    def launchAllRobots(self, current, previous):
        self.launchEtcRobots(current, previous)
        self.launchUsrHomeRobots(current, previous)
    def run(self):
        logger.info("Starting robot launcher thread: " + self.name)
        self.launchAllRobots(self.current, self.previous)
        logger.info("Stopping robot launcher thread: " + self.name)

class ClientListener(threading.Thread):
    def __init__ (self, nh, nl, conn):
        super(ClientListener, self).__init__()
        self.nh = nh
        self.nl = nl
        self.conn = conn
    def run (self):
        try:
            logger.info ("Starting client thread: " + self.name)
            self.conn.settimeout(5.0)
            reply = 'OK'
            data = self.conn.recv(1024)
            if data:
                logger.info("Got data: " + str(data))
                dataList = data.split(",")
                if dataList[0] == "postValueNotification":
                    self.nh.postValueNotification(dataList[1], dataList[2], dataList[3], dataList[4])
                if dataList[0] == "postBatteryValueNotification":
                    self.nh.postBatteryValueNotification(dataList[1], dataList[2], dataList[3], dataList[4])
                if dataList[0] == "postNodeEventNotification":
                    self.nh.postNodeEventNotification(dataList[1], dataList[2], dataList[3], dataList[4])
                if dataList[0] == "postValueChangeNotification":
                    self.nh.postValueChangeNotification(dataList[1], dataList[2], dataList[3], dataList[4], dataList[5])
                if dataList[0] == "getNotificationFromNodeByIndex":
                    n = self.nh.getNotificationFromNodeByIndex(dataList[1], dataList[2])
                    reply = pickle.dumps(n)
                if dataList[0] == "getEarliestNotificationOfCurrentState":
                    n = self.nh.getEarliestNotificationOfCurrentState(dataList[1])
                    reply = pickle.dumps(n)
                if dataList[0] == "getNotificationFromNodeById":
                    n = self.nh.getNotificationFromNodeById(dataList[1], dataList[2])
                    logger.info("Got notification by ID: " + str(n))
                    reply = pickle.dumps(n)
                if dataList[0] == "getNodeReport":
                    reply = self.nh.getNodeReport(dataList[1])
                    # This can get rather large.
                    logger.info("Got Node Report " + str(reply))
                if dataList[0] == "die":
                    self.nl.stop()
                if dataList[0] == "dump":
                    report = self.nh.dump()
                    # We do not send this back over tcp
                    logger.info(report)
            else:
                logger.info("Got no data")
        finally:
            self.conn.send(reply)
            self.conn.close()
            logger.info("Client Thread dying: " + self.name)
    def stop(self):
        self.conn.close()

class NotificationListener(threading.Thread):
    def __init__ (self, nh, port):
        super(NotificationListener, self).__init__()
        self.nh = nh
        self.PORT = port 
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.kill_received = False
        self.children = []

    def run(self):
        logger.info( "Starting listener thread: " + self.name)
        HOST = ''   # Symbolic name meaning all available interfaces
        #Bind socket to local host and port
        try:
            logger.info( "Binding on port: " + str(self.PORT))
            self.s.bind((HOST, self.PORT))
        except socket.error as msg:
            logger.info( 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            print( 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            return
        print( 'Socket bind complete')
        logger.info( 'Socket bind complete')

        #Start listening on socket
        self.s.listen(10)
        logger.info('Socket now listening')
        while not self.kill_received:
            try:
                #wait to accept a connection - blocking call
                conn, addr = self.s.accept()
                logger.info( 'Connected with ' + addr[0] + ':' + str(addr[1]))
                cl = ClientListener(self.nh, self, conn)
                cl.daemon = True
                cl.start()
                self.children.append(cl)
            except Exception as e:
                logger.info( 'Socket no longer listening: ' + str(e))
                break
        logger.info( "NotificationListener is dead: " + self.name)
    def stop(self):
        logger.info( "Closing NotificationListener")
        for child in self.children:
            child.stop()
        self.kill_received = True
        #Interrupt thread.
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('localhost', 55555))
            msg = "interrupt"
            s.send(msg)
            s.close()
        except:
            pass
        finally:
            logger.info("Closing main socket on port " + str(self.PORT))
            self.s.close()
    def waitForChildren(self):
        logger.info("Waiting on any children")
        [child.join() for child in self.children]
        logger.info("All children dead!")

class NotificationHandler:
    def __init__ (self):
        self.lock = threading.RLock() 
        self.PORT = 55555
        self.ignoreSeconds = 5
        self.maxNotifcationsPerNode = 20
        self.shelf = shelve.open(get_absolute_path(shelfLocation))
        self.mainNotificationListenerThread = None
        self.robotLaunchers = []
    def dump(self):
        report = ""
        with self.lock:
            for key in self.shelf.keys():
                ncb = self.shelf.get(key, None)
                if ncb is not None:
                    report += "Node ID: " + key + "\n"
                    report += "  Battery level: " + str(ncb.batteryValue) + "\n"
                    report += "  Last Wakeup Time: " + str(ncb.lastWakeupTime) + "\n"
                    report += "  Notifications:\n"
                    for notification in ncb.notifications:
                        report += "    " + str(notification) + "\n"
        return report
    def getNodeReport(self, nodeId):
        report = ""
        with self.lock:
            ncb = self.shelf.get(nodeId, None)
            if ncb is not None:
                report += "Node ID: " + nodeId + "\n"
                report += "  Battery level: " + str(ncb.batteryValue) + "\n"
                report += "  Last Wakeup Time: " + str(ncb.lastWakeupTime) + "\n"
                report += "  Notifications:\n"
                for notification in ncb.notifications:
                    report += "    " + str(notification) + "\n"
        return report 
    def postBatteryValueNotification (self, nodeId, commandClass, fullHex, value):
        notification = BatteryValueNotification(nodeId, commandClass, fullHex, value)
        logger.info("Created " + str(notification))
        self.postNotification(nodeId, notification)
    def postValueNotification (self, nodeId, commandClass, fullHex, value):
        notification = ValueNotification(nodeId, commandClass, fullHex, value)
        logger.info("Created " + str(notification))
        self.postNotification(nodeId, notification)
    def postValueChangeNotification (self, nodeId, commandClass, fullHex, value, previousValue):
        notification = ValueChangeNotification(nodeId, commandClass, fullHex, value, previousValue)
        logger.info("Created " + str(notification))
        self.postNotification(nodeId, notification)
    def postNodeEventNotification (self, nodeId, commandClass, fullHex, event):
        notification = NodeEventNotification(nodeId, commandClass, fullHex, event)
        logger.info("Created " + str(notification))
        self.postNotification(nodeId, notification)
    def postNotification (self, nodeId, notification):
        with self.lock:
            #Critical Section
            nodeIdStr = str(nodeId)
            previous = self.getLatestNotificationFromNode (nodeIdStr)
            logger.info("Got latest notification to be: " + str(previous))

            if previous is not None:
                diff = notification.time - previous.time
                diffSeconds = diff.total_seconds()
                logger.info("Last notification arrived " + str(diffSeconds) + " seconds ago")

                if (diffSeconds <= self.ignoreSeconds):
                    if (notification.value == previous.value) :
                        logger.info("Ignoring notification: " + str(notification.nid) + " since previous notification with same value came " + str(diffSeconds) + " seconds ago.")
                        notification.ignore = True

                if notification.value == 'False':
                    if previous.value == 'False':
                        # If a sensor is closed, and it is still closed, we
                        # do not really care about it.
                        # However, if a sensor is open, we care about it no
                        # matter what the previous state was.
                        logger.info("Ignoring notification: " + str(notification.nid) + " since previous notification was false and current notification is false")
                        notification.ignore = True
            else:
                logger.info("Making a dummy previous")
                previous = ValueNotification(notification.nodeId, notification.commandClass, notification.fullHex, "False")
                previous.time = datetime(1970, 1, 1)

            ncb = self.shelf.get(nodeIdStr, NodeControlBlock(nodeIdStr))
            l = ncb.notifications
            # Truncate list to maxNotifcationsPerNode size
            l.insert(0,notification)
            if len(l)>self.maxNotifcationsPerNode:
                ncb.notifications = l[:self.maxNotifcationsPerNode]
            self.shelf[nodeIdStr] = ncb
            self.shelf.sync()
            #End critical section
        # The following code cannot be in the critical section, because it
        # dump and getNodeReport (or any robot apis) can lock.
        if notification.ignore is False:
            r = RobotLauncher(notification, previous)
            r.daemon = True
            r.start()
            self.robotLaunchers.append(r)
    def getNotificationFromNodeByIndex (self, nodeId, index):
        indexInt = int(index)
        nodeIdStr = str(nodeId)
        logger.info("From node(" + nodeIdStr + ") getting notification at index[" + str(index) + "]")
        ncb = self.shelf.get(nodeIdStr, None)
        if not ncb:
            logger.info("no ncb")
            return None
        else: 
            l = ncb.notifications
            if indexInt >= len(l):
                logger.info( "length is short: " + str(len(l)))
                return None
            return l[indexInt]
    def getNotificationFromNodeById (self, nodeId, notificationId):
        nodeIdStr = str(nodeId)
        logger.info("From node(" + nodeIdStr + ") getting notification with nid[" + str(notificationId) + "]")
        ncb = self.shelf.get(nodeIdStr, None)
        if not ncb:
            logger.info("no ncb")
            return None
        else: 
            for notification in ncb.notifications:
                if notificationId == notification.nid:
                    logger.info("Found notification: " + str(notification))
                    return notification
            return None
    def getEarliestNotificationOfCurrentState (self, nodeId):
        notification = self.getNotificationFromNodeByIndex(nodeId, 0)
        if notification is not None:
            for i in range(1, self.maxNotifcationsPerNode): 
                n = self.getNotificationFromNodeByIndex(nodeId, i)
                if n and n.value == notification.value:
                    notification = n
                else:
                    break
        return notification
    def getLatestNotificationFromNode (self, nodeId):
        notification = self.getNotificationFromNodeByIndex(nodeId, 0)
        i = 1
        while (notification is not None) and (notification.ignore is True) and (i < self.maxNotifcationsPerNode):
            notification = self.getNotificationFromNodeByIndex(nodeId, i)
            i += 1
        return notification
    def getAllNotificationsFromNode(self, nodeId):
        nodeIdStr = str(nodeId)
        ncb = self.shelf.get(nodeIdStr, None)
        if ncb is None:
            return []
        else:
            return ncb.notifications
    def waitForRobotLaunchers (self):
        logger.info("Waiting on any robot launchers")
        [robotLauncher.join() for robotLauncher in self.robotLaunchers]
        logger.info("All robotLaunchers dead!")
    def start (self):
        self.mainNotificationListenerThread = NotificationListener(self, self.PORT)
        self.mainNotificationListenerThread.daemon = True
        self.mainNotificationListenerThread.start()
    def stop(self):
        logger.info("Stopping NotificationHandler")
        self.shelf.close()
        self.waitForRobotLaunchers()
        self.mainNotificationListenerThread.stop()
        self.mainNotificationListenerThread.waitForChildren()
        self.mainNotificationListenerThread.join()
        logger.info("NotificationHandler dead.")

def getNotificationFromNodeByIndex(nodeId, index, logger=getNotificationHandlerLogger()):
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('localhost', 55555))
        msg = "getNotificationFromNodeByIndex," + str(nodeId) + "," + str(index)
        logger.info("sending msg: " + msg)
        s.send(msg)
        n = s.recv(1024)
        return pickle.loads(n)
    finally:
        s.close()

def getNotificationFromNodeById(nodeId, id, logger=getNotificationHandlerLogger()):
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('localhost', 55555))
        msg = "getNotificationFromNodeById," + str(nodeId) + "," + id
        logger.info("sending msg: " + msg)
        s.send(msg)
        n = s.recv(1024)
        return pickle.loads(n)
    finally:
        s.close()

def getLatestNotification(nodeId, logger=getNotificationHandlerLogger()):
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('localhost', 55555))
        msg = "getNotificationFromNodeByIndex," + str(nodeId) + ",0"
        logger.info("sending msg: " + msg)
        s.send(msg)
        n = s.recv(1024)
        return pickle.loads(n)
    finally:
        s.close()

def getEarliestNotificationOfCurrentState(nodeId, logger=getNotificationHandlerLogger()):
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('localhost', 55555))
        msg = "getEarliestNotificationOfCurrentState," + str(nodeId)
        logger.info("sending msg: " + msg)
        s.send(msg)
        n = s.recv(1024)
        return pickle.loads(n)
    finally:
        s.close()

def getNodeReport(nodeId, logger=getNotificationHandlerLogger()):
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('localhost', 55555))
        msg = "getNodeReport," + str(nodeId)
        logger.info("sending msg: " + msg)
        s.send(msg)
        report = s.recv(10240)
        return report 
    finally:
        s.close()

def sendMsg (*args):
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('localhost', 55555))
        msg = ",".join(args)
        print("Sending msg: " + msg)
        s.send(msg)
        reply = s.recv(1024)
        print("Rxd reply: " + reply)
    finally:
        s.close()

def main():
    global logger
    nh = None
    try:
        logger = setupNotificationHandlerLogger()
        print("Starting NotificationHandler on this beautiful day " + str(datetime.datetime.now()))
        logger.info("Starting NotificationHandler on this beautiful day " + str(datetime.datetime.now()))
        nh = NotificationHandler()
        nh.start()
        while True: 
            sleep(1)
    except KeyboardInterrupt as e:
        logger.info( "Keyboard interrupt:" + str(e))
        if nh is not None:
            nh.stop()
    except Exception as e:
        print str(e)
        logger.info( "Unexpected error:" + str(e) )
        if nh is not None:
            nh.stop()

if __name__ == '__main__':
    main()

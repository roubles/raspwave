#!/usr/bin/env python

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

logger = None

class Notification:
    def __init__ (self, nodeId, state, event, value, commandClass, fullHex, time, ignore):
        self.nodeId = nodeId
        self.state = state
        self.event = event
        self.value = value
        self.commandClass = commandClass
        self.fullHex = fullHex
        self.time = time
        self.ignore = ignore

    def spaceSeparated(self):
        return " " + str(self.nodeId) + " " + str(self.state) + " " + str(self.event) + " " + str(self.value) + " " + str(self.commandClass) + " " + str(self.fullHex) + " \"" + str(self.time) + "\""

    def __str__ (self):
        return "Notification nodeId=[" + str(self.nodeId) + "], state=[" + str(self.state) + "] event=[" + str(self.event) + "], value=[" + str(self.value) + "], commandClass=[" + str(self.commandClass) + "], fullHex=[" + str(self.fullHex) + "], time=[" + str(self.time) + "], ignore=[" + str(self.ignore) + "]"

class RobotLauncher(threading.Thread):
    def __init__ (self, previous, current):
        super(RobotLauncher, self).__init__()
        self.ignoreSeconds = 5
        self.etcFolder = '/etc/raspwave/robots'
        self.usrHomeFolder = '~/.raspwave/robots'
        self.current = current
        self.previous = previous
    def launchRobots(self, folder, notification):
        logger.info("Launching all robots in folder: " + folder)
        if os.path.isdir(folder):
            for filename in os.listdir(folder):
                if filename.endswith(".py"):
                    cmd = "/usr/local/bin/raspscpt " + folder + '/' + filename + notification.spaceSeparated()
                    logger.info(cmd)
                    subprocess.call(cmd, shell=True)
    def launchEtcRobots(self, notification):
        self.launchRobots(self.etcFolder, notification)
    def launchUsrHomeRobots(self, notification):
        self.launchRobots(self.usrHomeFolder, notification)
    def launchAllRobots(self, notification):
        self.launchEtcRobots(notification)
        self.launchUsrHomeRobots(notification)
    def run(self):
        logger.info("Starting robot launcher thread: " + self.name)
        currentSecondsSinceEpoch = time.mktime(self.current.time.timetuple())
        if self.previous:
            previousSecondsSinceEpoch = time.mktime(self.previous.time.timetuple())
            diff = currentSecondsSinceEpoch - previousSecondsSinceEpoch
            logger.info("Last notification arrived " + str(diff) + " seconds ago")
            if (diff <= self.ignoreSeconds):
                if (self.current.value == self.previous.value) :
                    logger.info("Ignoring notification: " + str(self.current) + " since previous notification with same value came " + str(diff) + " seconds ago.")
                    self.current.ignore = True
        if self.current.ignore == False:
            self.launchAllRobots(self.current)
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
                if dataList[0] == "postNotification":
                    self.nh.postNotification(dataList[1], dataList[2], dataList[3], dataList[4], dataList[5], dataList[6])
                if dataList[0] == "getNotification":
                    n = self.nh.getNotificationFromNode(dataList[1], dataList[2])
                    reply = pickle.dumps(n)
                if dataList[0] == "die":
                    self.nl.stop()
                if dataList[0] == "dump":
                    self.nh.dump()
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
            return
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
            self.s.close()
    def waitForChildren(self):
        logger.info("Waiting on any children")
        [child.join() for child in self.children]

class NotificationHandler:
    def __init__ (self):
        self.PORT =55555
        self.maxNotifcationsPerNode = 10
        self.shelfLocation = '/etc/raspwave/db/nh.shelf'
        self.shelf = shelve.open(self.shelfLocation)
        self.mainNotificationListenerThread = None
        self.robotLaunchers = []
    def dump(self):
        for key in self.shelf.keys():
            logger.info("Node ID: " + key)
            l = self.shelf.get(key, [])
            for notification in l:
                logger.info("    " + str(notification))
    def postNotification (self, nodeId, state, event, value, commandClass, fullHex):
        nodeIdStr = str(nodeId)
        l = self.shelf.get(nodeIdStr, [])
        notification = Notification(nodeId, state, event, value, commandClass, fullHex, datetime.datetime.now(), False)
        previous = self.getLatestNotificationFromNode (nodeIdStr)

        # Truncate list to maxNotifcationsPerNode size
        l.insert(0,notification)
        if len(l)>self.maxNotifcationsPerNode:
            l = l[:self.maxNotifcationsPerNode]
        self.shelf[nodeIdStr] = l

        r = RobotLauncher(previous, notification)
        r.daemon = True
        r.start()
        self.robotLaunchers.append(r)
    def getNotificationFromNode (self, nodeId, index):
        indexInt = int(index)
        nodeIdStr = str(nodeId)
        logger.info("From node(" + nodeIdStr + ") getting notification[" + str(index) + "]")
        l = self.shelf.get(nodeIdStr, None)
        if not l:
            logger.info( "no list")
            return None
        if indexInt >= len(l):
            logger.info( "length is short: " + str(len(l)))
            return None
        return l[indexInt]
    def getLatestNotificationFromNode (self, nodeId):
        return self.getNotificationFromNode(nodeId, 0)
    def getAllNotificationsFromNode(self, nodeId):
        nodeIdStr = str(nodeId)
        return self.shelf.get(nodeIdStr, [])
    def start (self):
        self.mainNotificationListenerThread = NotificationListener(self, self.PORT)
        self.mainNotificationListenerThread.daemon = True
        self.mainNotificationListenerThread.start()
    def stop(self):
        logger.info( "Stopping NotificationHandler")
        self.shelf.close()
        self.mainNotificationListenerThread.stop()
        self.mainNotificationListenerThread.waitForChildren()
        self.mainNotificationListenerThread.join()

def setupLogger (name, logfile, verbose, stdout):
    global logger

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if stdout is True:
        #create a steam handler
        stdouthandler = logging.StreamHandler(sys.stdout)
        if verbose:
            stdouthandler.setLevel(logging.DEBUG)
        else:
            stdouthandler.setLevel(logging.INFO)

        # create a logging format for stdout
        stdoutformatter = logging.Formatter('%(message)s')
        stdouthandler.setFormatter(stdoutformatter)

        # add the stdout handler to the logger
        logger.addHandler(stdouthandler)

    if logfile is not None:
        # create a file handler
        filehandler = logging.FileHandler(logfile)
        if verbose:
            filehandler.setLevel(logging.DEBUG)
        else:
            filehandler.setLevel(logging.INFO)

        # create a logging format for the log file
        formatter = logging.Formatter('%(asctime)s - %(thread)d - %(message)s')
        filehandler.setFormatter(formatter)

        # add the file handler to the logger
        logger.addHandler(filehandler)

def getNotification(logger, nodeId, index):
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('localhost', 55555))
        msg = "getNotification," + str(nodeId) + "," + str(index)
        logger.info("sending msg: " + msg)
        s.send(msg)
        n = s.recv(1024)
        return pickle.loads(n)
    finally:
        s.close()

def getLatestNotification(logger, nodeId):
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('localhost', 55555))
        msg = "getNotification," + str(nodeId) + ",0"
        logger.info("sending msg: " + msg)
        s.send(msg)
        n = s.recv(1024)
        return pickle.loads(n)
    finally:
        s.close()

def getNodeReport(logger, nodeId):
    report = ""
    i = 0
    while True:
        n = getNotification(logger, nodeId, i)
        if n is not None:
            report += str(n) + "\n"
        else:
            break
        i = i + 1
    return report 

def postNotification(*args):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 55555))
    msg = "postNotification," + ",".join(args)
    print("sending msg: " + msg)
    s.send(msg)
    reply = s.recv(1024)
    print("Rxd reply: " + reply)
    return reply

def main():
    nh = None
    try:
        setupLogger("cronbots", "/var/log/raspwave/cronbots.log", True, False)
        setupLogger("robots", "/var/log/raspwave/robots.log", True, False)
        setupLogger(__name__, "/var/log/raspwave/notification.log", True, False)
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
        logger.info( "Unexpected error:" + str(e) )
        if nh is not None:
            nh.stop()

if __name__ == '__main__':
    main()

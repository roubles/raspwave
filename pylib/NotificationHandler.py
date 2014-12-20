#!/usr/bin/env python

import sys
import shelve
import datetime
import socket
from time import sleep
from thread import *

class Notification:
    def __init__ (self, nodeId, value, commandClass, fullHex, time):
        self.nodeId = nodeId
        self.value = value
        self.commandClass = commandClass
        self.fullHex = fullHex
        self.time = time

    def __str__ (self):
        return "Notification nodeId=[" + str(self.nodeId) + "], value=[" + str(self.value) + "], commandClass=[" + str(self.commandClass) + "], fullHex=[" + str(self.fullHex) + "], time=[" + str(self.time) + "]"

class NotificationHandler:
    def __init__ (self):
        self.PORT = 55555 
        self.maxNotifcationsPerNode = 10
        self.shelf = shelve.open('test_shelf.db')
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def postNotification (self, nodeId, value, commandClass, fullHex):
        nodeIdStr = str(nodeId)
        l = self.shelf.get(nodeIdStr, [])
        notification = Notification(nodeId, value, commandClass, fullHex, datetime.datetime.now())

        # Truncate list to maxNotifcationsPerNode size
        l.insert(0,notification)
        if len(l)>self.maxNotifcationsPerNode:
            l = l[:self.maxNotifcationsPerNode]
        self.shelf[nodeIdStr] = l

    def getNotificationFromNode (self, nodeId, index):
        nodeIdStr = str(nodeId)
        l = self.shelf.get(nodeIdStr, None)
        if not l:
            return None
        if index>=len(l):
            return None
        return l[index]

    def getLatestNotificationFromNode (self, nodeId):
        return self.getNotificationFromNode(nodeId, 0)

    def getAllNotificationsFromNode(self, nodeId):
        nodeIdStr = str(nodeId)
        return self.shelf.get(nodeIdStr, [])

    def clientthread(self, conn):
        data = conn.recv(1024)
        if data: 
            print "Got data: " + str(data)
            dataList = data.split(",")
            if dataList[0] is "postNotification":
                self.postNotification(dataList[1], dataList[2], dataList[3], dataList[4])
        conn.close()

    def listen(self):
        HOST = ''   # Symbolic name meaning all available interfaces
        #Bind socket to local host and port
        try:
            print "binding on port: " + str(self.PORT)
            self.s.bind((HOST, self.PORT))
        except socket.error as msg:
            print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            self.sys.exit()
        print 'Socket bind complete'
         
        #Start listening on socket
        self.s.listen(10)
        print 'Socket now listening'
        while True:
            try:
                print "accepting"
                #wait to accept a connection - blocking call
                conn, addr = self.s.accept()
                print 'Connected with ' + addr[0] + ':' + str(addr[1])
                start_new_thread(self.clientthread, (conn,))
            except:
                print 'socket no longer listening' 
                break
            print "I'm outta here"

    def start (self):
        start_new_thread(self.listen, ())

    def close(self):
        print "Closing NotificationHandler"
        self.shelf.close()
        self.s.close() #This should interrupt the self.s.accept() but it does not
        
def main():
    nh = NotificationHandler()
    nh.start()
    nh.postNotification(4, 0, 32, 1)
    nh.postNotification(4, 0, 32, 2)
    nh.postNotification(4, 0, 32, 3)
    for n in nh.getAllNotificationsFromNode(4):
        print str(n)
    sleep(100)
    nh.close()
    sleep(10)

if __name__ == '__main__':
    main()

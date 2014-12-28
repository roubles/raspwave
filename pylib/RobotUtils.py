#!/usr/bin/env python
# @author rouble matta

import logging
import logging.handlers
import argparse
import signal
import sys
import os
import anydbm
import subprocess
import ConfigParser
from time import sleep
from NotificationHandler import setupLogger

def setupRobotLogger ():
    return setupLogger("robots", "/var/log/raspwave/robots.log", True, False)

def convert_timedelta_str(duration):
    hours, minutes, seconds = convert_timedelta(duration)
    return '{} hours, {} minutes, {} seconds'.format(hours, minutes, seconds)

def convert_timedelta(duration):
    days, seconds = duration.days, duration.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    return hours, minutes, seconds

def robotsleep (logger, seconds):
    while (seconds):
        logger.info("Sleeping for " + seconds + " seconds")
        sleep(1)
        seconds--

def getCurrentAlarmStateDelayForNode(id):
    return getAlarmStateDelayForNode(id, getCurrentState())

def getCurrentAlarmState ():
    return readStringValue("STATE")

def getAlarmStateDelayForNode (id, state):
    config = ConfigParser.ConfigParser()
    config.read("/etc/raspwave/conf/nodes.conf")
    delay = config.get(id, state + "_DELAY") 
    return delay

def getNodes ():
    config = ConfigParser.ConfigParser()
    config.read("/etc/raspwave/conf/nodes.conf")
    return config.sections()

def getNodeName (id):
    config = ConfigParser.ConfigParser()
    config.read("/etc/raspwave/conf/nodes.conf")
    return config.get(id, "NAME")

def sendEmail (logger, emailAddresses, subject, body):
    for emailAddress in emailAddresses:
        logger.info("Sending email to " + emailAddress)
        p1 = subprocess.Popen(['/bin/echo', body], stdout=subprocess.PIPE) #Set up the echo command and direct the output to a pipe
        p2 = subprocess.Popen(['/usr/bin/mail', '-s', subject, emailAddress], stdin=p1.stdout) #send p1's output to p2
        p1.stdout.close() #make sure we close the output so p2 doesn't hang waiting for more input
        output = p2.communicate()[0] #run our commands

def readStringValue (key):
    strings = anydbm.open("/etc/raspwave/db/strings.cache.db", 'c')
    value = strings[key]
    strings.close()
    return value

def writeStringValue (key, value):
    strings = anydbm.open("/etc/raspwave/db/strings.cache.db", 'c')
    strings[key] = value
    strings.close()

def get_absolute_path (path):
    if path is None:
        return path
    return os.path.abspath(os.path.expandvars(os.path.expanduser(path)))

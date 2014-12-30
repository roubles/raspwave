#!/usr/bin/env python

import datetime
from NotificationHandler import getEarliestNotificationOfCurrentState,getNodeReport
from LoggerUtils import setupCronbotLogger
from ConfUtils import getNodeName,getNodes
from Utils import convert_timedelta_str
from RobotUtils import sendEmail

logger = setupCronbotLogger()

mailto = ["rouble@gmail.com"]
maxOpenTimeInSeconds = 240
now = datetime.datetime.now()

for node in getNodes():
    #TODO: if node type is door window sensor
    name = getNodeName(node)
    logger.info("Testing node: " + node + ":" + name)

    notification = getEarliestNotificationOfCurrentState(node, logger)
    if not notification:
        logger.info("No notifications for node: " + name)
    elif (notification.value == 'False'):
        delta = now - notification.time
        logger.info(name + " has been closed for " + convert_timedelta_str(delta))
    elif (notification.value == 'True'):
        delta = now - notification.time
        logger.info(name + " has been open for " + convert_timedelta_str(delta))
        if delta.total_seconds() > maxOpenTimeInSeconds:
            subject = name + " has been open for " + convert_timedelta_str(delta) 
            sendEmail(mailto, subject, getNodeReport(node));
    else:
        logger.info("Can not determine state of: " + getNodeName(node) + " since it is [" + notification.value + "]")

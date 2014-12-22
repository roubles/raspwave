#!/usr/bin/env python

from RobotUtils import getNodes,getNodeName,sendEmail,convert_timedelta_str
from NotificationHandler import Notification,getNotification,getNodeReport,setupLogger
import datetime
import logging

setupLogger("cronbots", "/var/log/raspwave/cronbots.log", True, False)
logger = logging.getLogger("cronbots")

maxOpenTimeInSeconds = 240
now = datetime.datetime.now()

for node in getNodes():
    #TODO: if node type is door window sensor
    name = getNodeName(node)
    logger.info("Testing node: " + node + ":" + name)

    notification = getNotification(logger, node, 0)
    if not notification:
        logger.info("No notifications for node: " + name)
    elif (notification.state == 'close'):
        delta = now - notification.time
        logger.info(name + " has been closed for " + convert_timedelta_str(delta))
    elif (notification.state == 'open'):
        delta = now - notification.time
        logger.info(name + " has been open for " + convert_timedelta_str(delta))
        if delta.total_seconds() > maxOpenTimeInSeconds:
            subject = name + " has been open for " + convert_timedelta_str(delta) 
            logger.info(subject)
            sendEmail(["rouble@gmail.com"], subject, getNodeReport(logger, node));
    else:
        logger.info("Can not determine state of: " + getNodeName(node))

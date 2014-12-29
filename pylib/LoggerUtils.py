#!/usr/bin/env python
# @author rouble matta

import sys
import logging

robotsLoggerName = "robots"
cronbotsLoggerName = "cronbots"
notificationHandlerLoggerName = "notificationHandler"
securityLoggerName = "security"

securityLoggingFile = "/var/log/raspwave/security.log"
robotsLoggingFile = "/var/log/raspwave/robots.log"
cronbotsLoggingFile = "/var/log/raspwave/cronbots.log"
notificationHandlerLoggingFile = "/var/log/raspwave/notification.log"
allLoggingFile = "/var/log/raspwave/all.log"

securityLoggerSetup = False
robotLoggerSetup = False
cronbotLoggerSetup = False
notificationHandlerLoggerSetup = False

def setupLogger (logger, logfile, verbose, stdout, all=True):
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

    if all is True:
        # create a file handler
        filehandler = logging.FileHandler(allLoggingFile)
        if verbose:
            filehandler.setLevel(logging.DEBUG)
        else:
            filehandler.setLevel(logging.INFO)

        # create a logging format for the log file
        formatter = logging.Formatter('%(asctime)s - %(thread)d - %(message)s')
        filehandler.setFormatter(formatter)

        # add the file handler to the logger
        logger.addHandler(filehandler)
    return logger

def getRobotLogger ():
    return logging.getLogger(robotsLoggerName)

def getCronbotsLogger ():
    return logging.getLogger(cronbotsLoggerName)

def getNotificationHandlerLogger ():
    return logging.getLogger(notificationHandlerLoggerName)

def getSecurityLogger ():
    return logging.getLogger(securityLoggerName)

def setupRobotLogger ():
    global robotLoggerSetup

    if robotLoggerSetup:
        return getRobotLogger()

    robotLoggerSetup = True
    return setupLogger(getRobotLogger(), robotsLoggingFile, True, True, True)

def setupCronbotLogger ():
    global cronbotsLoggerSetup

    if cronbotsLoggerSetup:
        return getCronbotsLogger()

    cronbotsLoggerSetup = True
    return setupLogger(getCronbotsLogger(), cronbotsLoggingFile, True, True, True)

def setupNotificationHandlerLogger ():
    global notificationHandlerLoggerSetup

    if notificationHandlerLoggerSetup:
        return getNotificationHandlerLogger()

    notificationHandlerLoggerSetup = True
    return setupLogger(getNotificationHandlerLogger(), notificationHandlerLoggingFile, True, True, True)

def setupSecurityLogger ():
    global securityLoggerSetup

    if securityLoggerSetup:
        return getSecurityLogger()

    securityLoggerSetup = True
    return setupLogger(getSecurityLogger(), securityLoggingFile, True, True, True)

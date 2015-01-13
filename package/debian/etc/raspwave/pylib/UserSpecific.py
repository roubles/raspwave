#!/usr/bin/env python
# @author rouble matta
import os
from LoggerUtils import setupNotificationHandlerLogger
from Utils import get_absolute_path
from NotificationHandler import usrHomeScriptsFolder

logger = setupNotificationHandlerLogger()

beepFile = os.path.join(usrHomeScriptsFolder, 'beep.sh')
longBeepFile = os.path.join(usrHomeScriptsFolder, 'longbeep.sh')

def beep ():
    if os.path.isfile(beepFile):
        os.popen(beepFile)
    print "BEEP!"
    logger.info("BEEP!")

def beepbeep ():
    beep()
    beep()

def longbeep ():
    if os.path.isfile(longBeepFile):
        os.popen(longBeepFile)
    print "LONGBEEP!"
    logger.info("LONGBEEP!")

def longbeepbeep ():
    longbeep()
    longbeep()

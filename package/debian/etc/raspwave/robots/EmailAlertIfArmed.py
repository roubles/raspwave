#!/usr/bin/env python
# @author rouble matta

import sys
import logging

from RobotUtils import readStringValue, sendEmail
from NotificationHandler import setupLogger
import EmailAlertAlways

setupLogger("robots", "/var/log/raspwave/robots.log", True, False)
logger = logging.getLogger("robots")

def main (*args):
    if (readStringValue("STATE") != "ARMED"):
        logger.info("Not armed!")
        return 1
    return EmailAlertAlways.main(*args)

if __name__=='__main__':
    sys.exit(main(*sys.argv))

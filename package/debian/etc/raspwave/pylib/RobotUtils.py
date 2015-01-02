#!/usr/bin/env python
# @author rouble matta

import subprocess
from time import sleep
from LoggerUtils import setupRobotLogger

logger = setupRobotLogger()

def robotSleep (seconds, logger=setupRobotLogger()):
    secondsInt = int(seconds)
    while (secondsInt):
        logger.info("Sleeping for " + str(secondsInt) + " seconds")
        sleep(1)
        secondsInt -= 1

def sendEmail (emailAddresses, subject="no subject", body="no body", logger=setupRobotLogger()):
    for emailAddress in emailAddresses:
        logger.info("Sending email to " + emailAddress)
        p1 = subprocess.Popen(['/bin/echo', body], stdout=subprocess.PIPE) #Set up the echo command and direct the output to a pipe
        p2 = subprocess.Popen(['/usr/bin/mail', '-s', '[raspwave-alarm] ' + subject, emailAddress], stdin=p1.stdout) #send p1's output to p2
        p1.stdout.close() #make sure we close the output so p2 doesn't hang waiting for more input
        output = p2.communicate()[0] #run our commands

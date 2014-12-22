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

def convert_timedelta_str(duration):
    hours, minutes, seconds = convert_timedelta(duration)
    return '{} hours, {} minutes, {} seconds'.format(hours, minutes, seconds)

def convert_timedelta(duration):
    days, seconds = duration.days, duration.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    return hours, minutes, seconds

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

def setupLogger (logfile, verbose):
    global logger

    logger = logging.getLogger("FreewaveRobot")
    logger.setLevel(logging.DEBUG)

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
        # We store 5 backup files. Each file can be as big as it needs to be.
        filehandler = logging.handlers.RotatingFileHandler(logfile, backupCount=5)
        if verbose:
            filehandler.setLevel(logging.DEBUG)
        else:
            filehandler.setLevel(logging.INFO)

        # create a logging format for the log file
        formatter = logging.Formatter('%(asctime)s - %(thread)d - %(message)s')
        filehandler.setFormatter(formatter)

        # add the file handler to the logger
        logger.addHandler(filehandler)


def setupParser ():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-l", "--logfile", help="Logging file", action="store", default=None)
    parser.add_argument("-v", "--verbose", help="Enable verbose debugs (in addition to STDOUT)", action="store_true", default=False)
    return parser

def get_absolute_path (path):
    if path is None:
        return path
    return os.path.abspath(os.path.expandvars(os.path.expanduser(path)))

def signal_handler(signal, frame):
    logger.info("Caught signal. Dying.")
    sys.exit(2)

def crux ():
    logfile = None
    if args.logfile:
        logfile = get_absolute_path(args.logfile)
    setupLogger(logfile, args.verbose)

if __name__ == "__main__":  crux()

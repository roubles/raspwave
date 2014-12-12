#!/usr/bin/env python
# @author rouble matta

import sys
from RobotUtils import sendEmail, getNodeName

# Always send an email, regardless of armed state

def processSignalOnSensor(name, signal):
    if (signal == "255"):
        sendEmail(["rouble@gmail.com"],  name + " is open", "hello");
    elif (signal == "0") :
        sendEmail(["rouble@gmail.com"], name + " is closed", "hello");

def main(id, signal):
    processSignalOnSensor(getNodeName(id), signal)
    return 0

if __name__=='__main__':
    sys.exit(main(sys.argv[1], sys.argv[2]))

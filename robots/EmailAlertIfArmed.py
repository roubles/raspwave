#!/usr/bin/env python
# @author rouble matta

import sys
from RobotUtils import readStringValue, sendEmail

if (readStringValue("STATE") != "ARMED"):
    print "Not armed!"
    sys.exit(1)

def processSignalOnSensor(name):
    if (sys.argv[2] == "1"):
        sendEmail(["rouble@gmail.com", "prmehta@cisco.com"],  name + " is open", "hello");
    elif (sys.argv[2] == "0") :
        sendEmail(["rouble@gmail.com", "prmehta@cisco.com"], name + " is closed", "hello");

if (sys.argv[1] == "2"):
    processSignalOnSensor("Garage Door");
if (sys.argv[1] == "3"):
    processSignalOnSensor("Back Door");
if (sys.argv[1] == "4"):
    processSignalOnSensor("Front Door");
if (sys.argv[1] == "5"):
    processSignalOnSensor("Garage");


#!/usr/bin/env python
# @author rouble matta

import sys
from RobotUtils import readStringValue, sendEmail
import EmailAlertAlways

def main (id, signal):
    if (readStringValue("STATE") != "ARMED"):
        print "Not armed!"
        return 1
    return EmailAlertAlways.main(id, signal)

if __name__=='__main__':
    sys.exit(main(sys.argv[1], sys.argv[2]))

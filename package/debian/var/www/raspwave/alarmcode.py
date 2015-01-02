#!/usr/bin/env python
# @author rouble matta

import sys
import hashlib
sys.path.append('/etc/raspwave/pylib')
from SecurityUtils import getCurrentAlarmCode
from LoggerUtils import setupSecurityLogger

def testCode (arguments):
    code = ""
    currentAlarmCode = getCurrentAlarmCode()
    if currentAlarmCode is not None and currentAlarmCode is not "":
        if "code" in arguments:
            code = arguments["code"].value
            if (hashlib.md5(code).hexdigest() != getCurrentAlarmCode()):
                return (1,code)
            else:
                return (3,code)
        else:
            return (2,code)
    else:
        return (0,code)

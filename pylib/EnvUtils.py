#!/usr/bin/env python
# @author rouble matta

import os

def isTestEnvironment():
    try:
        if os.environ['TEST_RASPWAVE'] is not "":
            print "Is test environment!"
            return True
        else:
            return False
    except:
        return False

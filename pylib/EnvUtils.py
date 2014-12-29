#!/usr/bin/env python
# @author rouble matta

import os

def isTestEnvironment():
    if os.environ['TEST_RASPWAVE'] is not None:
        return True
    else:
        return False

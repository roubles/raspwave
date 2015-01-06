#!/usr/bin/python -u
# @author rouble matta

import sys
sys.path.append('/etc/raspwave/pylib')
import cgi, cgitb
import os
from commonstate import setDelayedState

cgitb.enable()

if __name__ == '__main__':
    setDelayedState('RELAXED')

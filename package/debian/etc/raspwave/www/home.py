#!/usr/bin/python -u
# @author rouble matta

import sys
sys.path.append('/etc/raspwave/pylib')
import cgi, cgitb
from commonstate import setDelayedState

cgitb.enable()

if __name__ == '__main__':
    setDelayedState('HOME')

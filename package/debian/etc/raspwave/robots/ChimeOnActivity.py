#!/usr/bin/env python
# @author rouble matta

import sys
from UserSpecific import beep
from ConfUtils import isDoorWindowOrMotion

def ChimeOnActivity():
    beep()

def crux(*args):
    if not isDoorWindowOrMotion(args[2]):
        return 1

    if args[1] != 'control':
        return 1

    ChimeOnActivity()
    return 0

if __name__=='__main__':
    sys.exit(crux(*sys.argv))

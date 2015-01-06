#!/usr/bin/python -u
# @author rouble matta

import os
import sys
import datetime
sys.path.append('/etc/raspwave/pylib')
from LoggerUtils import setupSecurityLogger
from SecurityUtils import setDesiredAlarmState,setDesiredAlarmStateDelay
from ConfUtils import getExitDelay

logger = setupSecurityLogger()

def setDelayedState (desiredState):
    exitDelay = getExitDelay(desiredState)
    print 'Content-Type: text/html'
    print # HTTP says you have to have a blank line between headers and content
    logger.info("Setting desired state " + desiredState + " after " + str(exitDelay) + " seconds " )

    # We must set the desired state here. So, that even if we launch the
    # remaining code in the background, the desired state is accurately
    # reflected
    setDesiredAlarmState(desiredState)
    setDesiredAlarmStateDelay(str(datetime.datetime.now() + datetime.timedelta(seconds=exitDelay)))
    if exitDelay < 2:
        # No need to background this.
        os.popen('/usr/local/bin/raspscpt /etc/raspwave/scripts/setDelayedAlarmState.py ' + desiredState + ' ' + str(exitDelay) + ' True')
    else:
        os.popen('/usr/local/bin/raspscpt /etc/raspwave/scripts/setDelayedAlarmState.py ' + desiredState + ' ' + str(exitDelay) + ' True&')
    print 'OK'

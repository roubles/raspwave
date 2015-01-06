#!/usr/bin/env python
# @author rouble matta

import os
import sys
sys.path.append('/etc/raspwave/pylib')
from LoggerUtils import setupSecurityLogger
import cgi, cgitb

cgitb.enable()

logger = setupSecurityLogger()

if __name__ == '__main__':
    infoText="Panic-ing from web interface."
    logger.info(infoText)
    os.popen('/usr/local/bin/raspscpt /etc/raspwave/scripts/panic.py \"' + infoText + '\"' )
    print 'Content-Type: text/html'
    print # HTTP says you have to have a blank line between headers and content
    print 'OK'

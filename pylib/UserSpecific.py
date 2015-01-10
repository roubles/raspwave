#!/usr/bin/env python
# @author rouble matta
import os

def beep ():
    os.popen('/usr/bin/ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@192.168.1.4  "/bin/echo 2 > /dev/ttyS1"')

def beepbeep ():
    beep()
    beep()

def longbeep ():
    os.popen('/usr/bin/ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@192.168.1.4  "/bin/echo 3 > /dev/ttyS1"')

def longbeepbeep ():
    longbeep()
    longbeep()

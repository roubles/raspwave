#!/usr/bin/env python
# @author rouble matta

import os
import datetime

def secondsLeft (then):
    now = datetime.datetime.now()
    return (then - now).total_seconds()

def secondsLeftFromString (desiredAlarmStateDelay):
    then = datetime.datetime.strptime(desiredAlarmStateDelay, "%Y-%m-%d %H:%M:%S.%f")
    return secondsLeft(then)

def getNowStr () :
    return str(datetime.datetime.now())

def convert_timedelta_str(duration):
    hours, minutes, seconds = convert_timedelta(duration)
    return '{} hours, {} minutes, {} seconds'.format(hours, minutes, seconds)

def convert_timedelta(duration):
    days, seconds = duration.days, duration.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    return hours, minutes, seconds

def getTimeElapsed_HHMMSS(then):
    delta = datetime.datetime.now() - then
    return convert_timedelta_str(delta)

def get_absolute_path (path):
    if path is None:
        return path
    return os.path.abspath(os.path.expandvars(os.path.expanduser(path)))

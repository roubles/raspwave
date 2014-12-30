#!/usr/bin/env python
# @author rouble matta

import os
import datetime

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

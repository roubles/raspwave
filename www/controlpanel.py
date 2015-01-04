#!/usr/bin/env python
# @author rouble matta

import sys
sys.path.append('/etc/raspwave/pylib')
import datetime
from SecurityUtils import getCurrentAlarmState,AlarmState,getDesiredAlarmState,getDesiredAlarmStateDelay,getDesiredAlarmStateDelayAsTime,getLastStateChangeTimeDelta,isPanic
from ConfUtils import getExitDelay,getHttpUsername,getHttpPassword
from Utils import convert_timedelta_str
import cgi, cgitb

cgitb.enable()

if __name__ == '__main__':
    print 'Content-Type: text/html'
    print # HTTP says you have to have a blank line between headers and content
    print '<!DOCTYPE html>'
    print '<html>'
    print '  <head>'
    print '    <meta http-equiv="refresh" content="30"/>'
    print '    <title> Raspwave Alarm Control Panel </title>'
    print '  </head>'
    print '  <body>'
    print '    <div id="main">'
    print '    <p id="message">'
    currentAlarmState = getCurrentAlarmState()
    desiredAlarmState = getDesiredAlarmState()
    if currentAlarmState != desiredAlarmState:
        desiredAlarmStateDelay = getDesiredAlarmStateDelay()
        print 'Desired alarm state ' + desiredAlarmState + ' will be set after exit delay of ' + convert_timedelta_str(getDesiredAlarmStateDelayAsTime() - datetime.datetime.now())  + ' at ' + desiredAlarmStateDelay
    else:
        lastStateChangeTimeDelay = getLastStateChangeTimeDelta()
        print 'Current alarm state ' + currentAlarmState + ' has been set for ' + convert_timedelta_str(lastStateChangeTimeDelay)
    print '    </p>'
    print '    <form>'
    print '      <h3> Alarm State </h3>'
    for state in AlarmState:
        color = ""
        if desiredAlarmState == state:
            color = "color:grey;border-style:inset;" 
        if currentAlarmState == state:
            color = "color:red;border-style:inset;" 
        print '      <button id="' + state + '" onClick=\'setState("' + state +'")\' style="' + color + 'font: bold 60px Arial">' + state + '</button>'
        if state == "DISARMED":
            print '      Alarm Code:'
            print '      <input type="password" id="AlarmCodeDisarmed" style="font: bold 60px Arial" maxlength="10" size="8">' 
        print '      <br><br>'
    print '      <h3> Panic/UnPanic</h3>'
    color = ""
    if isPanic():
        color = "color:red;border-style:inset;" 
    print '      <button id="PANIC" onClick=\'panic("PANIC")\' style="' + color + 'font: bold 60px Arial">PANIC</button>'
    print '      <br><br>'
    print '      <button id="UNPANIC" onClick=\'panic("UNPANIC")\' style="font: bold 60px Arial">UNPANIC</button>'
    print '      Alarm Code:'
    print '      <input type="password" id="AlarmCodeUnpanic" style="font: bold 60px Arial" maxlength="10" size="8">' 
    print '      <br><br>'
    print '      </form>'
    print '      <h3> Detailed Status</h3>'
    print '      <button id="STATUS" onClick="window.location=\'http://irouble.synology.me:8443/raspwave/currentstate.py\'" style="font: bold 30px Arial">Status</button>'
    print '      <button id= "DETAILSTATUS" onClick="window.location=\'http://irouble.synology.me:8443/raspwave/alarm_status.py\'" style="font: bold 30px Arial">Detail Status</button>'
    print '      <button iD="NODEREPORT" onClick="window.location=\'http://irouble.synology.me:8443/raspwave/report.py\'" style="font: bold 30px Arial">Node Report</button>'
    print '    </div>'
    print '  <style>'
    print '    html, body {'
    print '      height: 100%;'
    print '      width: 100%;'
    print '    }'
    print '    p.message {'
    print '      border-style: dotted solid;'
    print '      border-color: red;'
    print '    }'
    print '  </style>'
    print '<script>'
    print 'function clearAllButtonColors ()'
    print '{'
    for state in AlarmState:
        print '    document.getElementById("' + state + '").style.color = "black";'
    print '}'
    print 'function setState(state)'
    print '{'
    print '    clearAllButtonColors()'
    print '    document.getElementById(state).style.color = "red";'
    print '    var xmlHttp = null;'
    print '    xmlHttp = new XMLHttpRequest();'
    print '    if (state == "DISARMED") {'
    print '        xmlHttp.open( "GET", "http://irouble.synology.me:8443/raspwave/" + state.toLowerCase() + ".py?code=" + document.getElementById("AlarmCodeDisarmed").value, false);'
    print '    } else { '
    print '        xmlHttp.open( "GET", "http://irouble.synology.me:8443/raspwave/" + state.toLowerCase() + ".py", false);'
    print '    }'
    print '    xmlHttp.send( null );'
    print '    if (state == "DISARMED") {'
    print '        if (xmlHttp.responseText.indexOf("Valid code") == -1) {'
    print '            alert("Invalid code! Not disarming.");'
    print '        }'
    print '    }'
    print '    return xmlHttp.responseText;'
    print '}'
    print 'function panic(state)'
    print '{'
    print '    document.getElementById(state).style.color = "red";'
    print '    var xmlHttp = null;'
    print '    xmlHttp = new XMLHttpRequest();'
    print '    if (state == "UNPANIC") {'
    print '        xmlHttp.open( "GET", "http://irouble.synology.me:8443/raspwave/" + state.toLowerCase() + ".py?code=" + document.getElementById("AlarmCodeUnpanic").value, false);'
    print '    } else { '
    print '        xmlHttp.open( "GET", "http://irouble.synology.me:8443/raspwave/" + state.toLowerCase() + ".py", false);'
    print '    }'
    print '    xmlHttp.send( null );'
    print '    if (state == "UNPANIC") {'
    print '        if (xmlHttp.responseText.indexOf("Valid code") == -1) {'
    print '            alert("Invalid code! Not unpanicing.");'
    print '        }'
    print '    }'
    print '    return xmlHttp.responseText;'
    print '}'
    print '</script>'
    print '</html>'

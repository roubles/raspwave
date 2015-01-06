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
    print '    <title> Raspwave Alarm Control Panel </title>'
    print '  </head>'
    print '  <body onload=\'launchRedraw(\"messageAndState\")\'>'
#    print '  <body>'
    print '    <div id="main">'
    print '    <p id="message">'
    currentAlarmState = getCurrentAlarmState()
    desiredAlarmState = getDesiredAlarmState()
    if currentAlarmState != desiredAlarmState:
        desiredAlarmStateDelay = getDesiredAlarmStateDelay()
        print 'Desired alarm state ' + desiredAlarmState + ' will be set after exit delay of ' + convert_timedelta_str(getDesiredAlarmStateDelayAsTime() - datetime.datetime.now())  + ' at ' + desiredAlarmStateDelay
    print '    </p>'
    print '    <form>'
    print '      <h3> Alarm State </h3>'
    for state in AlarmState:
        color = ""
        if desiredAlarmState == state:
            #color = "color:grey;border-style:inset;" 
            color = "color:grey;" 
        if currentAlarmState == state:
            #color = "color:red;border-style:inset;" 
            color = "color:red;" 
        print '      <button type="button" id="' + state + '" onClick=\'setState("' + state +'")\' style="' + color + 'font: bold 60px Arial">' + state + '</button>'
        if state == "DISARMED":
            print '      Alarm Code:'
            print '      <input type="password" id="AlarmCodeDisarmed" style="font: bold 60px Arial" maxlength="10" size="8">' 
        print '      <br><br>'
    print '      <h3> Panic/UnPanic</h3>'
    color = ""
    if isPanic():
        #color = "color:red;border-style:inset;" 
        color = "color:red;" 
    print '      <button type="button" id="PANIC" onClick=\'panic("PANIC")\' style="' + color + 'font: bold 60px Arial">PANIC</button>'
    print '      <br><br>'
    print '      <button type="button" id="UNPANIC" onClick=\'panic("UNPANIC")\' style="font: bold 60px Arial">UNPANIC</button>'
    print '      Alarm Code:'
    print '      <input type="password" id="AlarmCodeUnpanic" style="font: bold 60px Arial" maxlength="10" size="8">' 
    print '      <br><br>'
    print '      </form>'
    print '      <h3> Detailed Status</h3>'
    print '      <button id="ALARMSTATUS" onClick="window.location=\'http://irouble.synology.me:8443/raspwave/alarmstatus.py\'" style="font: bold 30px Arial">Alarm Status</button>'
    print '      <button id= "DETAILALARMSTATUS" onClick="window.location=\'http://irouble.synology.me:8443/raspwave/detailalarmstatus.py\'" style="font: bold 30px Arial">Detail Alarm Status</button>'
    print '      <br><br>'
    print '      <button iD="NODEREPORT" onClick="window.location=\'http://irouble.synology.me:8443/raspwave/nodereport.py\'" style="font: bold 30px Arial">Node Report</button>'
    print '      <button iD="DETAILNODEREPORT" onClick="window.location=\'http://irouble.synology.me:8443/raspwave/detailnodereport.py\'" style="font: bold 30px Arial">Detail Node Report</button>'
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
    print '    launchRedraw("messageAndState");'
    print '    if (state == "DISARMED") {'
    print '      launchRedraw("panic");'
    print '    }'
    #print '    setTimeout(function() {launchRedraw("messageAndState");},2000);'
    print '}'
    print 'function panic(state)'
    print '{'
    print '    document.getElementById(state).style.color = "red";'
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
    print '    launchRedraw("panic");'
    print '}'
    print 'function launchRedraw (selector) {'
#    print '  var desiredAlarmStateDelay = getState("desiredAlarmStateDelay");'
#    print '  window.desiredAlarmStateDelay = desiredAlarmStateDelay;'
    print '  function redrawMessageAndState()'
    print '  {'
    print '    document.getElementById("message").innerHTML = "";'
    print '    var exitDelayEndsInMs = 0;'
#    print '    var desiredAlarmStateDelay = getState("desiredAlarmStateDelay");'
#    print '    if (window.desiredAlarmStateDelay == desiredAlarmStateDelay) {'
#    print '      return;'
#    print '    }'
#    print '    window.desiredAlarmStateDelay = desiredAlarmStateDelay;'
    print '    var state = getState("currentAlarmStateAndDesiredAlarmState").split(" ");'
    print '    var currentAlarmState = state[0];'
    print '    var desiredAlarmState = state[1];'
    print '    if (currentAlarmState != desiredAlarmState) {'
    print '      var desiredAlarmStateDelay = getState("desiredAlarmStateDelay");'
    print '      var a = desiredAlarmStateDelay.split(/[^0-9]/);;'
    print '      exitDelayEndsInMs = new Date(a[0],a[1]-1,a[2],a[3],a[4],a[5]) - new Date();'
    print '      var message = "Desired alarm state " + desiredAlarmState + " will be set after exit delay of " + convert_timedelta_str(exitDelayEndsInMs)  + " at " + desiredAlarmStateDelay;'
    print '      document.getElementById("message").innerHTML = message;'
    print '      exitDelayEndsInMs += 4000; //for safe measure'
    print '    }'
    print '    clearAllButtonColors();'
    print '    if (currentAlarmState == desiredAlarmState) {'
    print '      document.getElementById(currentAlarmState).style.color = "red"; '
    #print '     document.getElementById(currentAlarmState).style.border-style = "inset"; '
    print '    } else {'
    print '      document.getElementById(currentAlarmState).style.color = "red"; '
    print '      document.getElementById(desiredAlarmState).style.color = "grey"; '
    #print '     document.getElementById(desiredAlarmState).style.border-style = "inset"; '
    print '    }'
    print '    return exitDelayEndsInMs;'
    print '  }'
    print '  function redrawPanic()'
    print '  {'
    print '    var isPanic = getState("isPanic");'
    print '    if (isPanic.toLowerCase() == "true") {'
    print '      document.getElementById("PANIC").style.color = "red"; '
    print '      document.getElementById("UNPANIC").style.color = "black"; '
    print '    } else {'
    print '      document.getElementById("PANIC").style.color = "black"; '
    print '      document.getElementById("UNPANIC").style.color = "black"; '
    print '    }'
    print '  }'
    print '  function convert_timedelta_str(milliseconds)'
    print '  {'
    print '    var totalSec = milliseconds / 1000;'
    print '    var hours = parseInt( totalSec / 3600 ) % 24;'
    print '    var minutes = parseInt( totalSec / 60 ) % 60;'
    print '    var seconds = Math.floor(totalSec % 60);'
    print '    var result = hours + " hours, " + minutes + " minutes, " + seconds + " seconds";'
    print '    return result;'
    print '  }'
    print '  function getState(key)'
    print '  {'
    print '    var xmlHttp = null;'
    print '    xmlHttp = new XMLHttpRequest();'
    print '    xmlHttp.open( "GET", "http://irouble.synology.me:8443/raspwave/state/" + key + ".py", false);'
    print '    xmlHttp.send( null );'
    print '    return xmlHttp.responseText.trim();'
    print '  }'
    print '  function getValue(key, text)'
    print '  {'
    print '    var myRegexStr = ".*" + key + ": (.*)"'
    print '    var re = new RegExp(myRegexStr,"g");'
    print '    var match = re.exec(text);'
    print '    return match[1];'
    print '  }'
    print '  if (selector == "messageAndState") {'
    print '    var exitDelayEndsInMs = redrawMessageAndState();'
    print '    if (exitDelayEndsInMs != 0) {'
#    print '      alert("will launch redrawMessageAndState in " + convert_timedelta_str(exitDelayEndsInMs))'
    print '      setTimeout(redrawMessageAndState, exitDelayEndsInMs);'
    print '    }'
    print '  } else if (selector == "panic") {'
    print '    redrawPanic();'
#    print '  } else if (selector == "loop") {'
#    print '    setInterval(redrawMessageAndState, 10000);'
    print '  }'
    print '}'
    print '</script>'
    print '</html>'

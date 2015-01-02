#!/usr/bin/env python
# @author rouble matta

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
    print '  <body>'
    print '    <div id="main">'
    print '      <h3> Alarm State </h3>'
    print '      <button onClick="window.location=\'http://irouble.synology.me:8443/raspwave/away.py\'" style="background-color:lightblue;font: bold 60px Arial">AWAY</button><br><br>'
    print '      <br><br>'
    print '      <button onClick="window.location=\'http://irouble.synology.me:8443/raspwave/home.py\'" style="background-color:lightblue;font: bold 60px Arial">HOME</button><br><br>'
    print '      <br><br>'
    print '      <button onClick="window.location=\'http://irouble.synology.me:8443/raspwave/relaxed.py\'" style="background-color:lightblue;font: bold 60px Arial">RELAXED</button><br><br>'
    print '      <br><br>'
    print '      <button onClick="window.location=\'http://irouble.synology.me:8443/raspwave/disarm.py?code=1234\'" style="background-color:lightgreen;font: bold 60px Arial">DISARM</button><br><br>'
    print '      <br><br>'
    print '      <h3> Panic/UnPanic</h3>'
    print '      <button onClick="window.location=\'http://irouble.synology.me:8443/raspwave/panic.py\'" style="background-color:red;font: bold 60px Arial">PANIC</button><br><br>'
    print '      <br><br>'
    print '      <button onClick="window.location=\'http://irouble.synology.me:8443/raspwave/unpanic.py?code=1234\'" style="background-color:lightgreen;font: bold 60px Arial">UNPANIC</button><br><br>'
    print '      <br><br>'
    print '    </div>'
    print '  <style>'
    print '    html, body {'
    print '      height: 100%;'
    print '      width: 100%;'
    print '    }'
    print '    #main {'
    print '      margin-right: auto         '            
    print '      margin-left: auto         '            
    print '      left: 0;'
    print '      min-height: 100%;'
    print '      width: 100%;'
    print '      position: absolute;'
    print '      overflow: auto;'
    print '    }'
    print '  </style>'
    print '</html>'

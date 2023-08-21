#!/usr/bin/env python
#----------------------------------------------------------------------------
# Name:         vcapp.py
# Purpose:      Simple framework for running individual VCollab applications
#
# Author:       Mohan Varma
#
# Created:      25-July-2008
# Copyright:    (c) 2008 by Visual Collaboration Technologies Inc.
# Licence:      VCollab license
#----------------------------------------------------------------------------

"""
This program will load and run one of the individual VCollab applications in 
this directory within its own frame window.  Just specify the application name
on the command line.
"""

import sys
sys.path.append('/usr/lib64/python2.4/site-packages')
import wx
import wx.lib.inspection
import wx.lib.mixins.inspection
import sys, os

import VMoveCAE
import CaeEngine

# stuff for debugging
#print "wx.version:", wx.version()
#print "pid:", os.getpid()
##raw_input("Press Enter...")

assertMode = wx.PYAPP_ASSERT_DIALOG
##assertMode = wx.PYAPP_ASSERT_EXCEPTION

#----------------------------------------------------------------------------

class Log:
    def WriteText(self, text):
        if text[-1:] == '\n':
            text = text[:-1]
        wx.LogMessage(text)
    write = WriteText

#----------------------------------------------------------------------------

class VCollabApp(wx.App, wx.lib.mixins.inspection.InspectionMixin):
    def __init__(self, name, appgui, engine):
        self.name = name
        self.appgui = appgui
        self.engine = engine
        wx.App.__init__(self, redirect=False)

    def OnInit(self):
        wx.Log_SetActiveTarget(wx.LogStderr())
        self.SetAssertMode(assertMode)
        self.Init()  # InspectionMixin

        #self.cfg = wx.Config(self.name)
        #if self.cfg.Exists('cwd'):
        #    try:
        #        os.chdir(self.cfg.Read('cwd'))
        #    except os.error, msg:
        #        self.cfg.Write('cwd', os.getcwd())

        license_status = self.engine.AcquireLicense()
        #license_status = True
        if 'False' == license_status:
            wx.MessageBox('\nLicense not available.\nExiting Application', 
                            'Error!')
            #return False

        else:
            self.frame = self.appgui.getNewFrame(self.engine)
            if self.frame:
                # so set the frame to a good size for showing stuff
                self.frame.Show(True)
                self.SetTopWindow(self.frame)

            else:
                # It was probably a dialog or something that is already
                # gone, so we're done.
                return False

        #wx.Log_SetActiveTarget(wx.LogStderr())
        #wx.Log_SetTraceMask(wx.TraceMessages)

        return True


    def OnExitApp(self, evt):
        #self.cfg.Write('cwd', os.getcwd())
        self.frame.Close(True)
        #self.cfg.Write('cwd', os.getcwd())

    def OnWidgetInspector(self, evt):
        wx.lib.inspection.InspectionTool().Show()

#----------------------------------------------------------------------------

def mainOld(argv):
    if len(argv) < 3:
        #print "Please specify a VCollab application name on the command-line"
        #raise SystemExit
        argv += ["VMoveCAE"]
        argv += ["CaeEngine"]

    guiname, guiext  = os.path.splitext(argv[1])
    appgui = __import__(guiname)
    enginename, engineext  = os.path.splitext(argv[2])
    appengine = __import__(enginename)

    #rc_file = name + '.rc'
    #for x in range(len(argv)-1):
    #    if argv[x] in ['--rc', '-rc']:
    #        rc_file = argv[x+1]
    #        break

    app = VCollabApp(guiname, appgui, appengine)
    app.MainLoop()
    license_status = appengine.getEngine().ReleaseLicense()

#----------------------------------------------------------------------------

def main(argv):
    os.environ["ABQ_CRTMALLOC"]="1"
    appengine = __import__('CaeEngine')
    engine = appengine.getEngine()

    file_list = []
    for option in argv:
        if not option.startswith('--'):
            file_list.append(option)

    if '--exclude-geometry' in argv:
        engine.ExcludeGeometry(True)

    if len(file_list) < 3:
        guiname = 'VMoveCAE'
        appgui = __import__(guiname)
        temp_dir = appengine.temp_dir()
        engine.SetLogFile(temp_dir + os.sep + 'vmovecae_trace.log')
        sys.stdout = open(temp_dir + os.sep + 'vmovecae.log', 'w')
        sys.stderr = open(temp_dir + os.sep + 'vmovecae_errors.log', 'w')
        app = VCollabApp(guiname, appgui, engine)
        app.MainLoop()
        engine.ReleaseLicense()
    else:
        batchname = 'VMoveCAEBatch'
        appbatch = __import__(batchname)
        appbatch.VMoveCAEBatch(engine, argv)

#----------------------------------------------------------------------------

if __name__ == "__main__":
    main(sys.argv)


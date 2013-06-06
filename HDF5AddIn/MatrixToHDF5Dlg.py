#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      SALAMANCA
#
# Created:     20.02.2013
# Copyright:   (c) SALAMANCA 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python
# -*- coding: utf-8 -*-


###############################################################################
#http://wiki.wxpython.org/AnotherTutorial#Examples

###############################################################################
import wx
import os
import sys
import VisumPy
import VisumPy.wxHelpers
from VisumPy.AddIn import AddIn, AddInState, AddInParameter
import VisumPy.helpers as helpers
import wx.lib.filebrowsebutton as wxfb

ID_MENU_NEW = wx.NewId()
ID_MENU_OPEN = wx.NewId()
ID_MENU_SAVE = wx.NewId()


class Example(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(Example, self).__init__(*args, **kwargs)

        self.InitUI()

    def onNewFile(self,evt):

        dialog = wx.FileDialog(None,'Choose a file',os.getcwd(),"", "",wx.OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            print dialog.GetPath()
        dialog.Destroy()

    def InitUI(self):
        #Panel und Box
        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        #Radiobuttons
        self.label_1 = wx.StaticText(pnl, -1, ("Zeitscheibe:"), pos= (15,15))
        self.z1 = wx.RadioButton(pnl, label='0-6', pos=(15, 30))
        self.Bind(wx.EVT_RADIOBUTTON, self.setVal, id=self.z1.GetId())
        self.z2 = wx.RadioButton(pnl, label='6-8', pos=(15, 45))
        self.Bind(wx.EVT_RADIOBUTTON, self.setVal, id=self.z2.GetId())
        self.z3 = wx.RadioButton(pnl, label='8-12', pos=(15, 60))
        self.Bind(wx.EVT_RADIOBUTTON, self.setVal, id=self.z3.GetId())
        self.z4 = wx.RadioButton(pnl, label='12-15', pos=(15, 75))
        self.Bind(wx.EVT_RADIOBUTTON, self.setVal, id=self.z4.GetId())
        self.z5 = wx.RadioButton(pnl, label='15-19', pos=(15, 90))
        self.Bind(wx.EVT_RADIOBUTTON, self.setVal, id=self.z5.GetId())
        self.z6 = wx.RadioButton(pnl, label='19-24', pos=(15, 105))
        self.Bind(wx.EVT_RADIOBUTTON, self.setVal, id=self.z6.GetId())
        self.z24 = wx.RadioButton(pnl, label='0-24', pos=(15, 125))
        self.Bind(wx.EVT_RADIOBUTTON, self.setVal, id=self.z24.GetId())

        #Get Projektverzeichniss
        matrix_verzeichnis = 69
        directory = Visum.GetPath(matrix_verzeichnis)

        self.openButton = wxfb.FileBrowseButton(pnl, buttonText = 'Speichern unter', labelText = '', labelWidth = 0,  fileMode=wx.SAVE, fileMask= '*.hdf5', startDirectory= directory ,  pos=(15,145))

        #Statusbar
        self.statusbar = self.CreateStatusBar(7)
        self.setVal(True)

        #Buttons
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, label='Ok')
        closeButton = wx.Button(self, label='Abbrechen')

        hbox2.Add(okButton)
        hbox2.Add(closeButton, flag=wx.LEFT, border=5)

        vbox.Add(pnl, proportion=1,
            flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(hbox2,
            flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)

        self.SetSizer(vbox)

        okButton.Bind(wx.EVT_BUTTON, self.OnOK) # Absenden der Abfrage - noch einfügen
        closeButton.Bind(wx.EVT_BUTTON, self.On_cancel)


        self.SetSize((300, 300))
        self.SetTitle('Nachfragemodell')
        self.Centre()
        self.Show(True)

    def On_cancel(self, event): # wxGlade: XLSParamsDlg.<event_handler>
        try:
            addInParam.SaveParameter(dict())
            addInParam.visumParameter.OK = False
            Parameter.OK = False
            Terminated.set()
        finally:
            self.Destroy()

    def OnOK(self, event):
        #Parameter zum Uebergeben
        param = dict()
        param["Zeitscheibe1"] = self.z1.GetValue()
        param["Zeitscheibe2"] = self.z2.GetValue()
        param["Zeitscheibe3"] = self.z3.GetValue()
        param["Zeitscheibe4"] = self.z4.GetValue()
        param["Zeitscheibe5"] = self.z5.GetValue()
        param["Zeitscheibe6"] = self.z6.GetValue()
        param["Zeitscheibe24"] = self.z24.GetValue()
        param["filepath"]=self.openButton.GetValue()

        addInParam.SaveParameter(param)
        if not addIn.IsInDebugMode:
            Terminated.set()
        else: # Start body script manually
            import MatricesToHDF5
        self.Destroy()
        ###testausgabe
##        x1 = param["filepath"]
##        frame = wx.Frame(None, title=x1)
##        frame.Show()

    # Show selected Data in Statusbar
    def setVal(self, event):
        state1 = str(self.z1.GetValue())  # returns true if selected
        state2 = str(self.z2.GetValue())
        state3 = str(self.z3.GetValue())
        state4 = str(self.z4.GetValue())
        state5 = str(self.z5.GetValue())
        state6 = str(self.z6.GetValue())
        state24 = str(self.z24.GetValue())
        self.statusbar.SetStatusText(state1,0)
        self.statusbar.SetStatusText(state2,1)
        self.statusbar.SetStatusText(state3,2)
        self.statusbar.SetStatusText(state4,3)
        self.statusbar.SetStatusText(state5,4)
        self.statusbar.SetStatusText(state6,5)
        self.statusbar.SetStatusText(state24,6)

if len(sys.argv) > 1:
    addIn = AddIn()
else:
    addIn = AddIn(Visum) # Erzeuge Visum Objekt


if addIn.IsInDebugMode:
    app = wx.PySimpleApp(0)
    Visum = addIn.VISUM
    addInParam = AddInParameter(addIn, None)
else:
    addInParam = AddInParameter(addIn, Parameter)

if addIn.State != AddInState.OK:
    addIn.ReportMessage(addIn.ErrorObjects[0].ErrorMessage)
else:
    try:
        wx.InitAllImageHandlers()

        dialog_1 = Example(None, -1, "TEST")
        app.SetTopWindow(dialog_1)
        dialog_1.Show()
        if addIn.IsInDebugMode:
            app.MainLoop()

    except:
        addIn.HandleException(addIn.TemplateText.MainApplicationError)
        if addIn.IsInDebugMode == False:
            Terminated.set()

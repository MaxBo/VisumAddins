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
import h5py


class getMatrix(wx.Dialog):

    filepath = ''

    def __init__(self, *args, **kwds):

        # begin wxGlade: XLSParamsDlg.__init__
        kwds["style"] = wx.CAPTION
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetSize((500,500))
        self.SetTitle('Nachfragematrizen einlesen')
        self.Centre()
        self.Show(True)

        self.header = wx.StaticText(self, -1, _(u'Nachfragematrix aus Datei in Visum einfügen'), pos=(15,15))

        #Get Projektverzeichnis
        matrix_verzeichnis = 69
        directory = Visum.GetPath(matrix_verzeichnis)

        self.openButton = wxfb.FileBrowseButton(self, buttonText = u'Öffen',
                                                labelText = u'Matrix öffnen:',
                                                labelWidth = 0,
                                                fileMode=wx.OPEN,
                                                fileMask= '*.hdf5; *.h5',
                                                startDirectory= directory ,
                                                pos=(15,50))

        self.auswahlButton = wx.Button(self, -1, _(u'Auswählen'), pos=(350, 50))
        self.Bind(wx.EVT_BUTTON, self.On_list, self.auswahlButton)

        self.label_1 = wx.StaticText(self, -1, (u"Tabelle auswählen: "), pos=(15, 100))
        self.label_1 = wx.StaticText(self, -1, ("Zeitscheibe:"), pos=(15, 125))
        self.z1 = wx.CheckBox(self, label='0-6', pos=(15, 140))
        self.Bind(wx.EVT_CHECKBOX, self.enable_24, id=self.z1.GetId())
        self.z2 = wx.CheckBox(self, label='6-8', pos=(15, 155))
        self.Bind(wx.EVT_CHECKBOX, self.enable_24, id=self.z2.GetId())
        self.z3 = wx.CheckBox(self, label='8-12', pos=(15, 170))
        self.Bind(wx.EVT_CHECKBOX, self.enable_24, id=self.z3.GetId())
        self.z4 = wx.CheckBox(self, label='12-15', pos=(15, 185))
        self.Bind(wx.EVT_CHECKBOX, self.enable_24, id=self.z4.GetId())
        self.z5 = wx.CheckBox(self, label='15-19', pos=(15, 200))
        self.Bind(wx.EVT_CHECKBOX, self.enable_24, id=self.z5.GetId())
        self.z6 = wx.CheckBox(self, label='19-24', pos=(15, 215))
        self.Bind(wx.EVT_CHECKBOX, self.enable_24, id=self.z6.GetId())
        self.z24 = wx.CheckBox(self, label='0-24', pos=(15, 230))
        self.Bind(wx.EVT_CHECKBOX, self.enable_16, id=self.z24.GetId())

        self.bez = wx.StaticText(self, -1, _(u'Parameter zur Speicherung in Visum'), pos=(15,250))
        self.code = wx.TextCtrl(self, -1, name='Code', pos=(100, 275))
        self.codelabel = wx.StaticText(self, -1, _(u'CODE'), pos=(15,275))
        self.no = wx.TextCtrl(self, -1, name='No', pos=(100, 300))
        self.nolabel = wx.StaticText(self, -1, _(u'NO'), pos=(15,300))
        self.name = wx.TextCtrl(self, -1, name='Name', pos=(100, 325))
        self.namelabel = wx.StaticText(self, -1, _(u'NAME'), pos=(15,325))

        # OK and Cancel
        self.btn_ok = wx.Button(self, -1, _("OK"), pos=(250, 420))
        self.btn_cancel = wx.Button(self, -1, _("Cancel"), pos=(350,420))

        self.Bind(wx.EVT_BUTTON, self.On_OK, self.btn_ok )
        self.Bind(wx.EVT_BUTTON, self.On_cancel, self.btn_cancel)



    def On_list(self, event): # Tabellen auswahl
        global filepath
        filepath = str(self.openButton.GetValue())
        f = h5py.File(filepath, 'r')
        c = list()
        items = f.items()

        for ch in items:
            cx = ch[0]
            c.append(cx)

        self.cMatrix = wx.ComboBox(self, -1,
                             choices=c,
                             style=wx.CB_DROPDOWN | wx.CB_DROPDOWN,
                             pos=(125,250))
        self.cMatrix.SetSelection(0)


    def enable_24(self, evt):
        self.z24.Enable(False)

    def enable_16(self, evt):
        self.z1.Enable(False)
        self.z2.Enable(False)
        self.z3.Enable(False)
        self.z4.Enable(False)
        self.z5.Enable(False)
        self.z6.Enable(False)

    def On_cancel(self, event): # wxGlade: XLSParamsDlg.<event_handler>
        try:
            addInParam.SaveParameter(dict())
            addInParam.visumParameter.OK = False
            Parameter.OK = False
            Terminated.set()
        finally:
            self.Destroy()

    def On_OK(self, event):
        #Parameter zum Uebergeben
        param = dict()
        param['filepath'] = filepath
        """why not defined?"""
        param['table'] = str(self.cMatrix.GetValue())

        addInParam.SaveParameter(param)
        if not addIn.IsInDebugMode:
            Terminated.set()
        else: # Start body script manually
            import GetMatrixBody
        self.Destroy()


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

        dialog_1 = getMatrix(None, -1, "TEST")
        app.SetTopWindow(dialog_1)
        dialog_1.Show()
        if addIn.IsInDebugMode:
            app.MainLoop()

    except:
        addIn.HandleException(addIn.TemplateText.MainApplicationError)
        if addIn.IsInDebugMode == False:
            Terminated.set()

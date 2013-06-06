#-------------------------------------------------------------------------------
# Name:        Nachfragematrizen einlesen
# Purpose:
#
# Author:      Nina Kohnen
#
# Created:     26.04.2013
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
import tables


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
                                                fileMask='*.h5',
                                                startDirectory= directory ,
                                                pos=(15,50))

        self.auswahlButton = wx.Button(self, -1, _(u'Auswählen'), pos=(350, 50))
        self.Bind(wx.EVT_BUTTON, self.On_list, self.auswahlButton)


        self.ovivText = wx.StaticText(self, -1, _(u'ÖV oder IV'), pos=(15,105))
        self.oviv = wx.ComboBox(self, -1,
                                choices=('OV', 'IV'),
                                style=wx.CB_DROPDOWN | wx.CB_DROPDOWN,
                                pos=(100,100))






        # OK and Cancel
        self.btn_ok = wx.Button(self, -1, _("OK"), pos=(250, 420))
        self.btn_cancel = wx.Button(self, -1, _("Cancel"), pos=(350,420))

        self.Bind(wx.EVT_BUTTON, self.On_OK, self.btn_ok )
        self.Bind(wx.EVT_BUTTON, self.On_cancel, self.btn_cancel)



    def On_list(self, event): # Tabellen auswahl
        global filepath
        filepath = str(self.openButton.GetValue())
        c=[]
        with tables.openFile(filepath, 'r') as f:
            nodes = f.listNodes(f.root) # tables unter root
            ts = f.root.modes_ts        # group = modes_ts

            for node in ts:
                cx = node.name
                c.append(cx)

        self.tableText = wx.StaticText(self, -1, _(u'Tabelle auswählen'), pos=(15,150))
        self.cMatrix = wx.ComboBox(self, -1,
                             choices=c,
                             style=wx.CB_DROPDOWN | wx.CB_DROPDOWN,
                             pos=(125,150))
        self.cMatrix.SetSelection(0)


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

        param['v'] = str(self.oviv.GetValue())

        table = str(self.cMatrix.GetValue())
        param['table'] = table

        addInParam.SaveParameter(param)
        if not addIn.IsInDebugMode:
            Terminated.set()
        else: # Start body script manually
            import GetNachfrageMatrixBody
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

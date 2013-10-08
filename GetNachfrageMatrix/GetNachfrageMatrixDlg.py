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

modes_en2de = {'put': u'1-OV',
         'car': u'2-Pkw-Fahrer',
         'passenger': u'3-Pkw-Mitfahrer',
         'bicycle': u'4-Fahrrad',
         'foot': u'5-zu Fuss',
         'all': u'0-Gesamtverkehr',
         }

modes_de2en = dict(zip(modes_en2de.values(), modes_en2de.keys()))
put_modes = ['put']

addin_path = os.path.join(os.getenv('APPDATA'), 'Visum', '125', 'Addins')
configpath = os.path.join(addin_path, 'demandConfig')


class getMatrix(wx.Dialog):

    filepath = ''

    def __init__(self, *args, **kwds):

        # begin wxGlade: XLSParamsDlg.__init__
        kwds["style"] = wx.CAPTION
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetSize((500,300))
        self.SetTitle('Nachfragematrizen einlesen')
        self.Centre()
        self.Show(True)

        self.header = wx.StaticText(self, -1, _(u'Nachfragematrix aus Datei in Visum einfügen'), pos=(15,15))
        self.header = wx.StaticText(self, -1, _(u'Die Zeitscheiben müssen für diese Funktion definiert sein'), pos=(15,30))

        #Get Projektverzeichnis
        matrix_verzeichnis = 69
        #directory = Visum.GetPath(matrix_verzeichnis)
        try:
            fn = os.path.join(configpath, 'project_folder.txt')
            with open(fn) as f:
                self.base_path = f.readline().strip()
        except IOError:
            self.base_path = r'W:\mobil\01 Projekte\1008 VEP Kassel\50 Modellaufbau\80 Nachfragedaten\kassel'

        self.directory = os.path.join(self.base_path, 'demand')

        self.openButton = wxfb.FileBrowseButton(self, buttonText = u'Öffnen',
                                                labelText = u'Matrix öffnen:',
                                                labelWidth = 0,
                                                fileMode=wx.OPEN,
                                                fileMask='*.h5;*.hdf5',
                                                startDirectory= self.directory ,
                                                pos=(15,50),
                                                changeCallback = self.On_list,
                                                )


        # OK and Cancel
        self.btn_ok = wx.Button(self, -1, _("OK"), pos=(250, 150))
        self.btn_cancel = wx.Button(self, -1, _("Cancel"), pos=(350,150))

        self.Bind(wx.EVT_BUTTON, self.On_OK, self.btn_ok )
        self.Bind(wx.EVT_BUTTON, self.On_cancel, self.btn_cancel)


    #def wxfbCallback(self):
        #"""
        #called when value in FileBrowseButton is changed
        #"""


    def On_list(self, event): # Tabellen auswahl
        global filepath
        filepath = str(self.openButton.GetValue())
        c=[]
        with tables.openFile(filepath, 'r') as f:
            ts = f.root.modes_ts        # group = modes_ts

            for node in ts:
                cx = node.name
                mode_name = modes_en2de[cx]
                c.append(mode_name)
            c.append('0-Gesamtverkehr')
        c.sort()

        self.tableText = wx.StaticText(self, -1,
                                       _(u'Tabelle auswählen:'),
                                       pos=(15,100))
        self.cMatrix = wx.ComboBox(self, -1,
                             choices=c,
                             style=wx.CB_DROPDOWN | wx.CB_DROPDOWN,
                             pos=(125,100),
                             )
        self.cMatrix.SetSelection(1)


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

        table_de = str(self.cMatrix.GetValue())
        table_en = modes_de2en[table_de]
        param['table'] = table_en

        if table_en == 'all':
            mode = 'Gesamt'
        elif table_en in put_modes:
            mode = 'OV'
        else:
            mode = 'IV'

        param['v'] = mode

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

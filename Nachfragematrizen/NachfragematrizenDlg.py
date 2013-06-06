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
from VisumPy.wxHelpers import wxNetobjCombo, wxAttrIDButton
from VisumPy.AddIn import AddIn, AddInState, AddInParameter
import VisumPy.helpers as helpers
import wx.lib.filebrowsebutton as wxfb
import win32api as win

def matrixFormatter(no, code):
    return "%d | %s" % (no, code)

class ParamsDlg(wx.Dialog):

    def __init__(self, *args, **kwds):

        # begin wxGlade: XLSParamsDlg.__init__
        kwds["style"] = wx.CAPTION
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetSize((500,500))
        self.SetTitle('Nachfragematrizen berechnen')


        #Input
        """Checkboxen"""
        self.kcalc = wx.CheckBox(self, label=u'Starte Kenngrößenberechnung und speichern als in HDF5',
                                 pos=(15,15))
        self.kcalc.SetValue(True)
        self.modelsplit = wx.CheckBox(self, label=u'Model Split/ Wegelängen neu kalibrieren',
                                      id=2,
                                      pos=(15,350))
        self.iv = wx.CheckBox(self, label=u'Rückkopplung mit IV Nachfrage',
                                      id=2,
                                      pos=(15,375))
        self.iv.SetValue(True)

        # Combo Box Config Files
        """Get *.py from Combobox and execute *.py"""
        self.label_conf = wx.StaticText(self, -1, _('Konfiguration'), pos=(15,50))
        choices = os.listdir(r'C:\Users\Public\Documents\VisumAddInTest')
        e_files = [f for f in choices if f.startswith('e')]
        self.cboMatrix = wx.ComboBox(self, -1,
                                     choices=e_files,
                                     style=wx.CB_DROPDOWN | wx.CB_DROPDOWN,
                                     pos=(100,50))
        self.cboMatrix.SetSelection(0)

        self.btn_conf = wx.Button(self, -1, _("Auswahl"), pos = (250, 50))
        self.Bind(wx.EVT_BUTTON, self.On_CONF, self.btn_conf)


        # Directories
        directory_kenn = r'W:\mobil\64 Zwischenablage Nina\Visum_Addins'
        directory_struktur = r'W:\mobil\64 Zwischenablage Nina\Visum_Addins'
        directory_szenario = r'W:\mobil\64 Zwischenablage Nina\Visum_Addins'
        directory = r'C:/Users/Public/Documents/VisumAddInTest'
        directory_confg = r'W:\mobil\64 Zwischenablage Nina\Visum_Addins'

        # Open File Buttons
        self.openKenn = wxfb.FileBrowseButton(self, buttonText = u'Öffnen',
                                              labelText = u'Kenngrößenmatrix',
                                              labelWidth = 200,
                                              fileMode=wx.OPEN,
                                              fileMask='*.h5',
                                              startDirectory=directory_kenn,
                                              pos=(125,100))
        # Set Value for Open Button -------- Soll in Config Datei ausgeführt werden
        self.openKenn.SetValue(u'W:\mobil\64 Zwischenablage Nina\Visum_Addins\24.hdf5')
        self.openStruktur = wxfb.FileBrowseButton(self, buttonText=u'Öffnen',
                                                  labelText=u'Strukturdaten       ',
                                                  labelWidth=200,
                                                  fileMode=wx.OPEN,
                                                  fileMask='*.h5',
                                                  startDirectory=directory_struktur ,
                                                  pos=(125,125))
        self.openSzenario = wxfb.FileBrowseButton(self, buttonText=u'Öffnen',
                                                  labelText=u'Szenario                 ',
                                                  labelWidth=200,
                                                  fileMode=wx.OPEN,
                                                  fileMask='*.h5',
                                                  startDirectory=directory_szenario,
                                                  pos=(125,150))


        """SET Szenario Name and Save"""
        self.label1 = wx.StaticText(self, -1, _("Szenario Namen:"), pos=(15, 260))
        self.name1 = wx.TextCtrl(self, -1,
                                size=(100, -1),
                                pos=(125,255))

        self.btn_name = wx.Button(self, -1, _("Auswahl"), pos = (230,255))
        self.Bind(wx.EVT_BUTTON, self.On_NAME, self.btn_name)
                # Save File Button
        self.saveButton = wxfb.FileBrowseButton(self, buttonText = u'Speichern unter',
                                                labelText = u'Szenario speichern:',
                                                labelWidth = 200,
                                                fileMode=wx.SAVE,
                                                fileMask= '*.h5',
                                                startDirectory=directory ,
                                                pos=(125,275))


        # OK and Cancel
        self.btn_ok = wx.Button(self, -1, _("OK"), pos = (250, 420))
        self.btn_cancel = wx.Button(self, -1, _("Cancel"), pos=(350,420))

        self.Bind(wx.EVT_BUTTON, self.On_OK, self.btn_ok )
        self.Bind(wx.EVT_BUTTON, self.On_cancel, self.btn_cancel)


    def On_CONF(self, event):
        # execute configuration
        directory = r'C:/Users/Public/Documents/VisumAddInTest'
        config = self.cboMatrix.GetValue()
        conf_path = directory + '/' + config
        execfile(conf_path)

    def On_NAME(self, event):
        name = self.name1.GetValue()
        win.MessageBox(0, name)
        directory = r'C:/Users/Public/Documents/VisumAddInTest/'
        self.saveButton.SetValue(directory+name+'.h5')


    def On_OK(self, event): # wxGlade: XLSParamsDlg.<event_handler>

        if self.openKenn.GetValue() == "":
            addIn.ReportMessage(_("Kenngerößenmatrix darf nicht leer sein.").decode('iso-8859-15'))


        # Parameter pass to Body
        param = dict()
            # Checkboxen
        param["hdf5_save"] = self.kcalc.GetValue()
        param["modelsplit"] = self.modelsplit.GetValue()
        param["iv"] = self.iv.GetValue()
            # HDF5 Filepaths
        param["Kanngrößenmatrizen"] = str(self.openKenn.GetValue())
        param["Strukturdaten"] = str(self.openStruktur.GetValue())
        param["Szenario"] = str(self.openSzenario.GetValue())
            # Speichern
        param["Name"] = str(self.name1.GetValue())
        param["Savepath"] = str(self.saveButton.GetValue())



        if not addIn.IsInDebugMode:
            Terminated.set()
        else: # Start body script manually
            import NachfragematrizenBody
        self.Destroy()

    def On_cancel(self, event): # wxGlade: XLSParamsDlg.<event_handler>
        try:
            addInParam.SaveParameter(dict())
            addInParam.visumParameter.OK = False
            Parameter.OK = False
            Terminated.set()
        finally:
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

        dialog_1 = ParamsDlg(None, -1, "Nachfragematrizen berechnen")
        app.SetTopWindow(dialog_1)
        dialog_1.Show()
        if addIn.IsInDebugMode:
            app.MainLoop()

    except:
        addIn.HandleException(addIn.TemplateText.MainApplicationError)
        if addIn.IsInDebugMode == False:
            Terminated.set()

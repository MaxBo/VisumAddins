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
from os import path
import sys
import VisumPy
from VisumPy.wxHelpers import wxNetobjCombo, wxAttrIDButton
from VisumPy.AddIn import AddIn, AddInState, AddInParameter
import VisumPy.helpers as helpers
import wx.lib.filebrowsebutton as wxfb
import win32api as win

configpath = r"\Visum\125\Addins\demandConfig"

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
        ##self.kcalc = wx.CheckBox(self, label=u'Starte Kenngrößenberechnung und speichern als in HDF5',
         ##                        pos=(15,15))
        ##self.kcalc.SetValue(True)
        self.modelsplit = wx.CheckBox(self, label=u'Model Split/ Wegelängen neu kalibrieren',
                                      id=2,
                                      pos=(15,350))
        #self.iv = wx.CheckBox(self, label=u'Rückkopplung mit IV Nachfrage',
                                      #id=2,
                                      #pos=(15,375))
        #self.iv.SetValue(True)

        # Combo Box Config Files
        """Get *.py from Combobox and execute *.py"""
        self.label_conf = wx.StaticText(self, -1, _('Konfiguration:'), pos=(15,50))
        choices = os.listdir(os.getenv('APPDATA')+configpath)
        e_files = [f for f in choices]
        self.cboMatrix = wx.ComboBox(self, -1,
                                     choices=e_files,
                                     size=(175, -1),
                                     style=wx.CB_DROPDOWN | wx.CB_DROPDOWN,
                                     pos=(100,45))
        self.cboMatrix.SetSelection(0)

        self.btn_conf = wx.Button(self, -1, _(u'Übernehmen'), pos = (280, 45))
        self.Bind(wx.EVT_BUTTON, self.On_CONF, self.btn_conf)


        # Directories
        directory_put = r'W:\mobil\01 Projekte\1008 VEP Kassel\50 Modellaufbau\80 Nachfragedaten\kassel\matrices\skims_put'
        directory_prt = r'W:\mobil\01 Projekte\1008 VEP Kassel\50 Modellaufbau\80 Nachfragedaten\kassel\matrices\skims_prt'
        directory_nmt = r'W:\mobil\01 Projekte\1008 VEP Kassel\50 Modellaufbau\80 Nachfragedaten\kassel\matrices\skims_nmt'
        #directory_struktur = r'W:\mobil\01 Projekte\1008 VEP Kassel\50 Modellaufbau\80 Nachfragedaten\kassel\params'
        directory_zonaldata = r'W:\mobil\01 Projekte\1008 VEP Kassel\50 Modellaufbau\80 Nachfragedaten\kassel\zonal_data'
        directory = r'C:/Users/Public/Documents/VisumAddInTest'
        directory_confg = r'W:\mobil\64 Zwischenablage Nina\Visum_Addins'

        # Open File Buttons
        self.openPut = wxfb.FileBrowseButton(self, buttonText = u'Öffnen',
                                              labelText = u'ÖV Kenngrößen:          ',
                                              labelWidth = 250,
                                              fileMode=wx.OPEN,
                                              fileMask='*.h5; *.hdf5',
                                              startDirectory=directory_put,
                                              pos=(50,125))
        # Set Value for Open Button -------- Soll in Config Datei ausgeführt werden
        self.openPrt = wxfb.FileBrowseButton(self, buttonText=u'Öffnen',
                                                  labelText=u'IV Kenngrößen:            ',
                                                  labelWidth=250,
                                                  fileMode=wx.OPEN,
                                                  fileMask='*.h5; *.hdf5',
                                                  startDirectory=directory_prt,
                                                  pos=(50,155))
        self.openNmt = wxfb.FileBrowseButton(self, buttonText=u'Öffnen',
                                                  labelText=u'NM Kenngrößen:         ',
                                                  labelWidth=250,
                                                  fileMode=wx.OPEN,
                                                  fileMask='*.h5; *.hdf5',
                                                  startDirectory=directory_nmt,
                                                  pos=(50,185))
        self.openStruktur = wxfb.FileBrowseButton(self, buttonText=u'Öffnen',
                                                  labelText=u'Strukturdaten:              ',
                                                  labelWidth=250,
                                                  fileMode=wx.OPEN,
                                                  fileMask='*.h5; *.hdf5',
                                                  startDirectory=directory_zonaldata ,
                                                  pos=(50,215))



        """SET Szenario Name and Save"""
        self.label1 = wx.StaticText(self, -1, _("Szenario Namen eingeben:"), pos=(15, 280))
        self.name1 = wx.TextCtrl(self, -1,
                                size=(200, -1),
                                pos=(175,275))


        # OK and Cancel
        self.btn_ok = wx.Button(self, -1, _("OK"), pos = (250, 420))
        self.btn_cancel = wx.Button(self, -1, _("Cancel"), pos=(350,420))

        self.Bind(wx.EVT_BUTTON, self.On_OK, self.btn_ok )
        self.Bind(wx.EVT_BUTTON, self.On_cancel, self.btn_cancel)


    def On_CONF(self, event):
        # execute configuration
        directory = os.path.join(os.getenv('APPDATA')+configpath)
        config = self.cboMatrix.GetValue()
        conf_path = directory + '/' + config
        execfile(conf_path)

    def On_NAME(self, event):
        name = self.name1.GetValue()
        #win.MessageBox(0, name)
        directory = os.path.join(os.getenv('APPDATA')+configpath)
        self.saveButton.SetValue(directory+name+'.h5')
        

    def On_OK(self, event): # wxGlade: XLSParamsDlg.<event_handler>

        if self.openPut.GetValue() == "":
            addIn.ReportMessage(_("ÖV Kenngrößenmatrix für darf nicht leer sein.").decode('iso-8859-15'))
            
                
        # Parameter pass to Body
        param = dict()
            # Checkboxen
        param["modelsplit"] = self.modelsplit.GetValue()
            #Modelsplit Warnung
        if param["modelsplit"] == True:
            dlg = wx.MessageDialog(self, 'Sind Sie sicher, dass Sie kalibrieren wollen?', 'Warnung', wx.YES_NO | wx.ICON_QUESTION)
            result = dlg.ShowModal()
            ##addIn.ReportMessage(_(str(result).decode('iso-8859-15')))
            if result == 5104:
                param["modelsplit"] = False

            # HDF5 Filepaths
        param["PUT"] = str(self.openPut.GetValue()).split('\\')[-1]
        param["PRT"] = str(self.openPrt.GetValue()).split('\\')[-1]
        param["NMT"] = str(self.openNmt.GetValue()).split('\\')[-1]
        param["Struktur"] = str(self.openStruktur.GetValue()).split('\\')[-1]
        param["Name"] = str(self.name1.GetValue())
        #param["Savepath"] = str(self.saveButton.GetValue())


        addInParam.SaveParameter(param)
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

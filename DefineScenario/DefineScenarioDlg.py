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


class ParamsDlg(wx.Dialog):
    """
    Parameter Dialog:
    Test ob Visum.Net.AttValue('ScenarioCode') in scenarios
    wenn ja: pass
    DropDown-Menu with all available scenarios
    Textfeld mit neuem Namen
    CreateScenario: Open ScenarioDialog
    """

    def __init__(self, *args, **kwds):

        # begin wxGlade: XLSParamsDlg.__init__
        kwds["style"] = wx.CAPTION
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetSize((500,500))
        self.SetTitle('Szenario auswählen')

        #Input
        """Checkboxen"""

        label = u'Neu kalibrieren am Modal Split'

        # Combo Box Config Files
        """Get *.py from Combobox and execute *.py"""
        self.label_conf = wx.StaticText(self, -1, _('Konfiguration:'),
                                        pos=(15,50))
        choices = os.listdir(configpath)
        e_files = [f for f in choices if f.endswith('.py')]
        self.cboMatrix = wx.ComboBox(self, -1,
                                     choices=e_files,
                                     size=(175, -1),
                                     style=wx.CB_DROPDOWN | wx.CB_DROPDOWN,
                                     pos=(100,45))
        self.cboMatrix.SetSelection(0)

        self.btn_conf = wx.Button(self, -1, _(u'Übernehmen'), pos = (280, 45))
        self.Bind(wx.EVT_BUTTON, self.On_CONF, self.btn_conf)


        # Directories
        # Hardcoding raus!!!
        try:
            fn = os.path.join(configpath, 'project_folder.txt')
            with open(fn) as f:
                base_path = f.readline().strip()
        except IOError:
            base_path = r'W:\mobil\01 Projekte\1008 VEP Kassel\50 Modellaufbau\80 Nachfragedaten\kassel'

        directory_put = os.path.join(base_path, 'matrices', 'skims_put')
        directory_prt = os.path.join(base_path, 'matrices', 'skims_prt')
        directory_nmt = os.path.join(base_path, 'matrices', 'skims_nmt')
        directory_zonaldata = os.path.join(base_path, 'zonal_data')
        directory_params = os.path.join(base_path, 'params')

        """SET Szenario Name and Save"""
        msg = "Szenario Namen eingeben:"
        self.label1 = wx.StaticText(self, -1, _(msg), pos=(15, 320))
        self.name1 = wx.TextCtrl(self, -1,
                                size=(200, -1),
                                pos=(175,315))


        # OK and Cancel
        self.btn_ok = wx.Button(self, -1, _("OK"), pos = (250, 420))
        self.btn_cancel = wx.Button(self, -1, _("Cancel"), pos=(350,420))

        self.Bind(wx.EVT_BUTTON, self.On_OK, self.btn_ok )
        self.Bind(wx.EVT_BUTTON, self.On_cancel, self.btn_cancel)


    def On_CONF(self, event):
        # execute configuration
        directory = os.path.join(configpath)
        config = self.cboMatrix.GetValue()
        conf_path = directory + '/' + config
        execfile(conf_path)

    def On_NAME(self, event):
        name = self.name1.GetValue()
        #win.MessageBox(0, name)
        directory = os.path.join(configpath)
        self.saveButton.SetValue(directory+name+'.h5')


    def On_OK(self, event): # wxGlade: XLSParamsDlg.<event_handler>

        if self.openPut.GetValue() == "":
            msg = "ÖV Kenngrößenmatrix für darf nicht leer sein."
            addIn.ReportMessage(_(msg).decode('iso-8859-15'))


        # Parameter pass to Body
        param = dict()
            # Checkboxen
        param["modal_split"] = self.modal_split.GetValue()
            #Modelsplit Warnung
        if param["modal_split"] == True:
            msg = 'Sind Sie sicher, dass Sie neu kalibrieren wollen?'
            dlg = wx.MessageDialog(self, msg, 'Warnung', wx.YES_NO | wx.ICON_QUESTION)
            result = dlg.ShowModal()
            ##addIn.ReportMessage(_(str(result).decode('iso-8859-15')))
            if result == 5104:
                param["modal_split"] = False

        param["Name"] = str(self.name1.GetValue())


        addInParam.SaveParameter(param)
        if not addIn.IsInDebugMode:
            Terminated.set()
        else: # Start body script manually
            import DefineScenarioBody
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

        dialog_1 = ParamsDlg(None, -1, "Nachfrage berechnen")
        app.SetTopWindow(dialog_1)
        dialog_1.Show()
        if addIn.IsInDebugMode:
            app.MainLoop()

    except:
        addIn.HandleException(addIn.TemplateText.MainApplicationError)
        if addIn.IsInDebugMode == False:
            Terminated.set()

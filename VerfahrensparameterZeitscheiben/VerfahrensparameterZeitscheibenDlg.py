#------------------------------------------------------------------------------
# Name:        Dialog for Importine TimeSlices
# Purpose:
#
# Author:      Max Bohnet
#
# Created:     20.02.2013
#------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

if __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import wx
import os
import sys
import VisumPy
import VisumPy.wxHelpers
from VisumPy.AddIn import AddIn, AddInState, AddInParameter
import VisumPy.helpers as helpers
#import wx.lib.filebrowsebutton as wxfb
from helpers.get_params import get_scenarios_from_visum
import tempfile


class Example(wx.Dialog):

    def __init__(self, *args, **kwds):

        kwds["style"] = wx.CAPTION
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetSize((300, 300))
        self.SetTitle('Zeitscheiben aus Szenario importieren')
        self.Centre()
        self.Show(True)

        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Szenario holen
        demand_scenarios = get_scenarios_from_visum(Visum)
        parametersets = ['Basisversion']
        project = Visum.ScenarioManagement.CurrentProject
        if project is None:
            raise ValueError('AddIn has to be started with a Scenario Management Project opened')
        for parameterset in project.ProcedureParameterSets:
            parametersets.append(parameterset.AttValue('Code'))
        #


        # Combo Box
        msg = u'Zeitscheibe aus folgendem \nNachfrageszenario importieren'
        self.label_2 = wx.StaticText(pnl,
                                     -1,
                                     _(msg),
                                     pos=(15,15),
                                     size=(200, -1))
        self.cboDemandScenario= wx.ComboBox(pnl, -1,
                                     choices=demand_scenarios,
                                     size=(150, -1),
                                     style=wx.CB_DROPDOWN | wx.CB_DROPDOWN,
                                     pos=(15,70))
        self.Bind(wx.EVT_COMBOBOX, self.select_demand_scenario,
                  self.cboDemandScenario)
        self.cboDemandScenario.SetValue(demand_scenarios[0])

        # Combo Box
        msg = u'Zeitscheiben in folgende \nVerfahrensparametersätze \nimportieren'
        self.label_3 = wx.StaticText(pnl,
                                    -1,
                                    _(msg),
                                    pos=(300,15),
                                     size=(200, -1))
        self.cboParameterSets= wx.CheckListBox(pnl, -1,
                                    choices=parametersets,
                                    size=(200, -1),
                                    style=wx.CB_DROPDOWN | wx.CB_DROPDOWN,
                                    pos=(300,70))
        self.Bind(wx.EVT_COMBOBOX, self.select_parametersets,
                  self.cboParameterSets)

        #Buttons
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        okButton = wx.Button(self, label='OK')
        closeButton = wx.Button(self, label='Abbrechen')

        hbox2.Add(okButton)
        hbox2.Add(closeButton, flag=wx.LEFT, border=5)

        vbox.Add(pnl, proportion=1,
                 flag=wx.ALL | wx.EXPAND, border=5)
        vbox.Add(hbox2,
                 flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        self.SetSizer(vbox)

        okButton.Bind(wx.EVT_BUTTON, self.OnOK)
        closeButton.Bind(wx.EVT_BUTTON, self.On_cancel)

        self.SetSize((600, 600))
        self.SetTitle(u'Zeitscheiben für Verfahrensparameter setzen')
        self.Centre()
        self.Show(True)


    def On_cancel(self, event):  # wxGlade: XLSParamsDlg.<event_handler>
        try:
            addInParam.SaveParameter(dict())
            addInParam.visumParameter.OK = False
            Parameter.OK = False
            Terminated.set()
        finally:
            self.Destroy()

    def OnOK(self, event):
        #Parameter zum Uebergeben
        selection = [self.cboParameterSets.IsChecked(i)
                     for i in range(self.cboParameterSets.GetCount())]
        param = {'demand_scenario' : self.cboDemandScenario.GetValue(),
                 'parametersets' : selection
                 ,}
        addInParam.SaveParameter(param)
        if not addIn.IsInDebugMode:
            Terminated.set()
        else:  # Start body script manually
            import VerfahrensparameterZeitscheibenBody
        self.Destroy()


    def select_parametersets(self, event):
        self.parametersets = self.cboParameterSets.GetSelection()
        print(self.cboParameterSets.GetCheckedItems())

    def select_demand_scenario(self, event):
        print(self.cboDemandScenario.GetValue())


    def enable_IV(self, evt):
        pass


if len(sys.argv) > 1:
    addIn = AddIn()
else:
    addIn = AddIn(Visum)  # Erzeuge Visum Objekt


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
        if addIn.IsInDebugMode is False:
            Terminated.set()

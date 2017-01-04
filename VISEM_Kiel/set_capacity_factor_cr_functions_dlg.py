#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
'''
VISUM add-in Set Capacity Factor

Date: 10.05.2015
Author: Martin Seeger
Contact: Martin.Seeger@ptvgroup.com
Company: PTV AG'''

# This file was generated from wxGlade file AddIn_Template.wxg
# and contains an add-in template for VISUM add-ins likewise
# instructions about how to change the add-in in wxGlade.
# The instruction will be displayed after the program start.
# The add-in has three buttons Help, OK and Cancel and the
# main design with flexGridSizers and spacers.
# When clicking the "Help"-Button a new help frame will be
# created and the content of the "Help.htm" will be displayed.

import wx
import wx.lib.agw.floatspin as FS
import os
import sys
import gettext

from VisumPy.AddIn import AddIn, AddInState, MessageType, AddInParameter


class SetCapacityFactor(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: SetCapacityFactor.__init__
        kwds["style"] = wx.CAPTION | wx.RESIZE_BORDER | wx.THICK_FRAME | wx.STAY_ON_TOP
        wx.Dialog.__init__(self, *args, **kwds)
        self.labelLink = wx.StaticText(self, wx.ID_ANY, _("Capacity Factor"))
        self.btnOK = wx.Button(self, wx.ID_ANY, _("OK"))
        self.btnCancel = wx.Button(self, wx.ID_ANY, _("Cancel"))
        
        self.floatspin = FS.FloatSpin(self, -1, pos=(50, 50), min_val=0.5, max_val=25,
                                 increment=0.5, value=11.0, agwStyle=FS.FS_RIGHT)
        self.floatspin.SetFormat("%f")
        self.floatspin.SetDigits(2)        

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.on_OK, self.btnOK)
        self.Bind(wx.EVT_BUTTON, self.on_cancel, self.btnCancel)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: PreprocessBalanceEpics.__set_properties
        self.SetTitle(_("Set Capacity Factor"))
        self.btnOK.SetDefault()
        # end wxGlade
        self.__setGuiParameter()

    def __do_layout(self):
        # begin wxGlade: PreprocessBalanceEpics.__do_layout
        grid_sizer_1 = wx.FlexGridSizer(2, 4, 0, 0)
        grid_buttons = wx.FlexGridSizer(1, 3, 0, 10)
        main_grid_sizer = wx.FlexGridSizer(2, 1, 20, 0)
        para_grid_sizer = wx.FlexGridSizer(1, 4, 5, 0)
        main_grid_sizer.Add(para_grid_sizer, 1, wx.EXPAND, 0)
        grid_sizer_1.Add((20, 20), 0, 0, 0)
        para_grid_sizer.Add(self.labelLink, 0, wx.ALIGN_CENTER_VERTICAL | wx.FIXED_MINSIZE, 0)
        para_grid_sizer.Add((10, 10), 0, wx.EXPAND, 0)
        para_grid_sizer.Add(self.floatspin, 0, wx.EXPAND, 0)
        grid_sizer_1.Add(main_grid_sizer, 1, wx.EXPAND, 0)
        grid_buttons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_buttons.Add(self.btnOK, 0, 0, 5)
        grid_buttons.Add(self.btnCancel, 0, 0, 5)
        grid_buttons.AddGrowableCol(1)
        grid_sizer_1.Add(grid_buttons, 1, wx.TOP | wx.EXPAND, 20)
        grid_sizer_1.Add((20, 20), 0, 0, 0)
        self.SetSizer(grid_sizer_1)
        grid_sizer_1.Fit(self)
        grid_sizer_1.AddGrowableRow(1)
        grid_sizer_1.AddGrowableCol(1)
        self.Layout()
        # end wxGlade
        self.SetBestFittingSize()
        xSize = self.GetSize().x
        ySize = self.GetSize().y
        self.SetMinSize((xSize, ySize))


    def __setGuiParameter(self):
        '''
        Write the Add-In parameters into the GUI elements
        '''
        defaultParam = {'Capacity_Factor': 11.0}
        param = addInParam.Check(False, defaultParam)
        self.floatspin.SetValue(param["Capacity_Factor"])
        self.labelLink.Enable()
        self.floatspin.Enable()


    def __setAddInParameter(self):
        '''
        Set the Add-In parameters from the GUI elements
        '''
        param = dict()
        param['Capacity_Factor'] = self.floatspin.GetValue()
        return param


    def on_help(self, event):  # wxGlade: PreprocessBalanceEpics.<event_handler>
        #Is executed when clicking on the "Help" button and opens
        #a htm-file with the help description of the add-in#
        try:
            os.startfile(addIn.DirectoryPath + _("Help.htm"))
        except:
            addIn.HandleException()

    def on_OK(self, event):  # wxGlade: PreprocessBalanceEpics.<event_handler>
        param = self.__setAddInParameter()

        addInParam.SaveParameter(param)
        if not addIn.IsInDebugMode:
            Terminated.set()
        self.Destroy()

    def on_cancel(self, event):  # wxGlade: PreprocessBalanceEpics.<event_handler>
        if not addIn.IsInDebugMode:
            Terminated.set()
        self.Destroy()



# end of class MyDialog
if len(sys.argv) > 1:
    addIn = AddIn()
else:
    addIn = AddIn(Visum)

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
        SetCapacityFactorDlg = SetCapacityFactor(None, -1, "")
        app.SetTopWindow(SetCapacityFactorDlg)
        SetCapacityFactorDlg.Show()

        if addIn.IsInDebugMode:
            app.MainLoop()
    except:
        addIn.HandleException(addIn.TemplateText.MainApplicationError)
        if not addIn.IsInDebugMode:
            Terminated.set()

#
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
# -*- coding: utf8 -*-

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


class Example(wx.Dialog):
    
    def __init__(self, *args, **kwds):
        
        kwds["style"] = wx.CAPTION
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetSize((500,300))
        self.SetTitle('Matrizen speichern')   
        
        # Combo Box 
        self.label_conf = wx.StaticText(self, -1, _(u'Matrix wählen:'), pos=(15,50))
        
        m = Visum.Net.Matrices.GetAll
        c=[]
        for matrix in m:
            d = matrix.AttValue('MatrixType')
            ##if d == 'MATRIXTYPE_DEMAND':
            m_code = matrix.AttValue('Code')
            m_no = matrix.AttValue('NO')
            app = str(m_no)+' '+m_code
            c.append(app)
                
        self.cboMatrix = wx.ComboBox(self, -1,
                                     choices= c,
                                     size=(175, -1),
                                     style=wx.CB_DROPDOWN | wx.CB_DROPDOWN,
                                     pos=(130,45))
        self.cboMatrix.SetSelection(0) 
        
        #Get Projektverzeichniss
        matrix_verzeichnis = 69
        directory = Visum.GetPath(matrix_verzeichnis)

        self.saveButton = wxfb.FileBrowseButton(self, buttonText = 'Speichern unter', 
                                                labelText = '', 
                                                labelWidth = 0,  
                                                fileMode=wx.SAVE,
                                                size=(300, -1),
                                                fileMask= '*.hdf5', 
                                                startDirectory= directory ,  
                                                pos=(15,100))        
        # OK and Cancel
        self.btn_ok = wx.Button(self, -1, _("OK"), pos=(250, 220))
        self.btn_cancel = wx.Button(self, -1, _("Cancel"), pos=(350,220))

        self.Bind(wx.EVT_BUTTON, self.On_OK, self.btn_ok )
        self.Bind(wx.EVT_BUTTON, self.On_cancel, self.btn_cancel)  
        
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
        param['matrix'] = self.cboMatrix.GetValue()
        param['file'] = str(self.saveButton.GetValue())

        addInParam.SaveParameter(param)
        if not addIn.IsInDebugMode:
            Terminated.set()
        else: # Start body script manually
            import SaveDemandMatrixBody
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

        dialog_1 = Example(None, -1, "TEST")
        app.SetTopWindow(dialog_1)
        dialog_1.Show()
        if addIn.IsInDebugMode:
            app.MainLoop()

    except:
        addIn.HandleException(addIn.TemplateText.MainApplicationError)
        if addIn.IsInDebugMode == False:
            Terminated.set()

# -*- coding: utf8 -*-
#-------------------------------------------------------------------------------
# Name:        Nachfragemodell anwerfen und Nachfragematrizen ausgeben
# Purpose:
#
# Author:      Nina Kohnen
#
# Created:     03.04.2013
# Copyright:   (c) Barcelona 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import numpy
import tables
import VisumPy
import os
import sys
import time
import VisumPy.AddIn
from VisumPy.helpers import GetMatrix , SetMatrix
from tables.exceptions import NoSuchNodeError
##from simcommon.helpers import latinize
import os.popen


def Run(param):
    #get parameter
    param["hdf5_save"] = kenn_calc_save
    param["modelsplit"] = modelsplit
    param["iv"] = iv
        # HDF5 Filepaths
    param["Kanngrößenmatrizen"] = kenn_path
    param["Strukturdaten"] = strukt_path
    param["Szenario"] = szen_path
        # Speichern
    param["Name"] = name
    param["Savepath"] = savepath

    if param["hdf5_save"]:
        # call AddIN
        operations = Visum.Procedures.Operations
        op = operations.AddOperation(1)
        op.SetAttValue('OperationType', 84)  # 84 = AddIn aber noch nicht defniert welches???
        opa = op.AddInParameters
        opa.SetAttValue('AddInID', 'GGR_CALCSAVESKIM')

##        execfile('C:\Users\Barcelona\AppData\Roaming\Visum\125\AddIns\CalculateSaveSkimmatrix\CalculateSaveSkimmatrix.vai')

    ##if param["modelsplit"]t:

    # Open Matrices
##    k = tables.openFile(kenn_path, 'r')
##    st = tables.openFile(strukt_path, 'r')
##    sz = tables.openFile(szen_path, 'r')

    # Nachfragemodell aufrufen
    so.system(nachfragemodell.py)



    # IV Modell starten
    ##if param["iv"]:
##    # subprocess
##        Popen.poll()

    # Progressdialog
    # return if terminated

# ADDIN
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
        defaultParam = {}

        param = addInParam.Check(True, defaultParam)
        Run(param)
    except:
        addIn.HandleException(addIn.TemplateText.MainApplicationError)

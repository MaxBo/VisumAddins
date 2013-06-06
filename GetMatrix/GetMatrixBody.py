# -*- coding: utf8 -*-
#-------------------------------------------------------------------------------
# Name:        VISUM Matrices to HDF5 for each time
# Purpose:
#
# Author:      Barcelona
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
import h5py


def Run(param):
    filepath = param['filepath']
    tablename = param['table']

    # number of existing matrices
    mx = Visum.Net.Matrices.GetAll
    number = len(mx)
    newn = number +1
    """Or highest number of existing Matrix?
    Oder Matrix vorher Manuell anlegen und Nummer angeben?"""
    # Create new demandmatrix
    a = Visum.Net.AddMatrix(newn)

    # Set DemandMatrix parameters
    """als variablen übergeben?"""
    a.SetAttValue('Name', 'Testname')
    a.SetAttValue('Code', 'Testcode')

### Get Values
##        ma = m.GetValues()
##        a = numpy.array(ma)

    # Open File
    with tables.openFile(filepath, 'a') as h:
        # HDF5 mit h5py (funktioniert z.Z. nur in 27)
        table = h[tablename]
        tt = table[z] # z = zeitscheibe ,
        arr = tt.value
        # Set Values
        a.SetValues(arr)
        """richtiges Format!!!???
        Zeitscheibe auswählen? ist da nötig bei Nachfragematrizen?"""


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

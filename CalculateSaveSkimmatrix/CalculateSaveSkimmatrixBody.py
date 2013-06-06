# -*- coding: utf8 -*-
#------------------------------------------------------------------------------
# Name:        VISUM Matrices to HDF5 for each time
# Purpose:
#
# Author:      Barcelona
#
# Created:     03.04.2013
# Copyright:   (c) Barcelona 2013
# Licence:     <your licence>
#------------------------------------------------------------------------------

import numpy
import tables
import VisumPy
import os
import sys
import time
#from simcommon.helpers import latinize
from latinze import latinize
import VisumPy.AddIn

from VisumPy.helpers import GetMatrix, SetMatrix
from tables.exceptions import NoSuchNodeError

i = []
# Zeitschiebe aus GUI
def Run(param):

    if param["Zeitscheibe1"]:
        i.append(0)
    if param["Zeitscheibe2"]:
        i.append(1)
    if param["Zeitscheibe3"]:
        i.append(2)
    if param["Zeitscheibe4"]:
        i.append(3)
    if param["Zeitscheibe5"]:
        i.append(4)
    if param["Zeitscheibe6"]:
        i.append(5)
##Was machen wir mit diesem FAll???
    if param["Zeitscheibe24"]:
        i.append(6)

    #File Path from MatrixToHDF5Dlg
    filepath = param['filepath']

    # For each i:
    for item in i:
        #Get start/end Time from Analysezeiträume
        """Zeitscheiben müssen vorher einmal als
        Analyseverfahrensparameter eingeladen werden."""
        ##Evtl. noch automatisieren
        f = Visum.Procedures.Functions
        at = f.AnalysisTimes
        a = at.TimeInterval(item + 1)  # auswahl Zeitinterval
        start = a.AttValue('StartTime')
        end = a.AttValue('EndTime')
        if item == 6:
            start = 0
            end = 2800*24-1

        #calculate Skimmatrix
        operations = Visum.Procedures.Operations
        op = operations.AddOperation(1)
        op.SetAttValue('OperationType', 102)
        # # In Tabelle auf S. 113/114 nachschauen
        put_ckmp = op.PuTCalcSkimMatrixParameters
        ttp = put_ckmp.TimetableBasedParameters
        ttbp = ttp.BaseParameters
        ttbp.SetTimeIntervalStart(start)  # Time in seconds
        ttbp.SetTimeIntervalEnd(end)    # Time in Seconds

        # Open File
        with tables.openFile(filepath, 'a') as h:

            #Alle Matrizen
            AllMatrices = Visum.Net.Matrices.GetAll

            for m in AllMatrices:

                m_type = m.AttValue('MatrixType')

                #Wenn Kenngroessenmatrix
                if m_type == 'MATRIXTYPE_SKIM':

                    #Create/Open HDF5
                    name = latinize(m.AttValue('Name'))
                    #name = m.AttValue('Name') # da latinize nur
                    code = m.AttValue('Code')
                    no = m.AttValue('No')

                    root = h.root
                    #Matrix als Numpy array (hat funktion shape)
                    data = VisumPy.helpers.GetMatrix(Visum, no)

                    addIn.ReportMessage(name)
                    try:
                        # Existiert der Knoten(Tabelle)
                        table_in_hdf5 = h.getNode(root, name)

                    except NoSuchNodeError:
                        # Wenn nicht :
                        m_shape = data.shape          # Get Shape
                        m_row = m_shape[0]             # Get Row Number
                        m_col = m_shape[1]              # Get Col Number
                        zeit = 6
                        # if 24 h
                        if item == 6:
                            zeit = 1
                        arr_shape = (zeit, m_row, m_col)

                        #Create Array (here)
                        arr = numpy.zeros(arr_shape, dtype='f4')

                        # create Table (in hdf5 file)
                        ##arrname = code+str(t)
                        table_in_hdf5 = h.createArray(root, name, arr)

                    # Fill table with Matrix
                    if item == 6:
                        table_in_hdf5[0] = data
                    else:
                        table_in_hdf5[item] = data

                    #Meta Infos (Node)
                    table_in_hdf5.attrs['Name'] = name
                    t = time.localtime()
                    date = time.asctime(t)
                    table_in_hdf5.attrs['Last Updated'] = date

                    #Set Attributes (root)
    ##                h.root._v_attrs['VISUM Version'] = inputdata

                    # Save
                    h.flush()

            # Tabelle Bezirke
            try:
                zonetable = h.getNode(h.root.Bezirke)
            except NoSuchNodeError:
                zones = Visum.Net.Zones
                nummer = numpy.array(VisumPy.helpers.GetMulti(zones, 'No'))
                name = numpy.array(VisumPy.helpers.GetMulti(zones, 'Name')).view(numpy.chararray).encode('cp1252')
                rec = numpy.rec.fromarrays([nummer, name],
                                           names=['zone_no',
                                                  'zone_name'],
                                           titles=['Bezirke', 'BezirksNamen'],
                                           formats=['<i4', 'S255'])
                zonetable = h.createTable(root, 'Bezirke', rec)

            h.flush()


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

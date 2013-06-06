# -*- coding: utf8 -*-
#-------------------------------------------------------------------------------
# Name:        Nachfragematrizen einlesen
# Purpose:
#
# Author:      Nina Kohnen
#
# Created:     26.04.2013
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
from VisumPy.helpers import GetMatrix , SetMatrix, GetMulti, __getMatrixByCode

from tables.exceptions import NoSuchNodeError
import h5py
from VisumPy.matrices import fromNumArray

#zeit = {0:'0006', 1:'0608', 2:'0812', 3:'1215', 4:'1519', 5:'1924'}

def Run(param):
    filepath = param['filepath']
    tablename = param['table']
    v = param['v']

    # Free Matrix NO
    matrices = Visum.Net.Matrices.GetAll
    all_numbers = set(range(1, 255))
    used_numbers = set([int(mat.AttValue('No')) for mat in matrices])
    free = all_numbers.difference(used_numbers)

    # Free Ganglinien NO
    gang = Visum.Net.TimeSeriesCont.GetAll
    all_gang = set(range(1, 25))
    used_gang = set([int(g.AttValue('No')) for g in gang])
    free_gang = all_gang.difference(used_gang)

    f = Visum.Procedures.Functions
    at = f.AnalysisTimes

    zeit = []

    for t in xrange(at.NumTimeIntervals):
        ti = at.TimeInterval(t+1)
        if not ti.AttValue('IsAggregate'):
            zeit.append(ti.AttValue('Code'))

    codes = GetMulti(Visum.Net.Matrices, 'Code')
    # Does Matrix exist?
    for z, code in enumerate(zeit):
        #ovcode = 'OV%s' %code.encode("iso-8859-15")
        ovcode = v+code.encode("iso-8859-15")
        if not ovcode in codes:
            # add Matrix
            no = free.pop()
            a = Visum.Net.AddMatrix(no)

            # Set DemandMatrix parameters
            a.SetAttValue('Name', v+code)
            a.SetAttValue('Code', v+code)
            a.SetAttValue('MatrixType', 'MATRIXTYPE_DEMAND')

        # Fill Matrix
        with tables.openFile(filepath, 'r') as h:
            try:
                table_in_hdf5 = h.getNode(h.root.modes_ts, tablename)
                zones = Visum.Net.Zones.GetAll
                tt = table_in_hdf5[z]
                f = fromNumArray(tt, zones)
                values = f['datavalues']
                SetMatrix(Visum, ovcode, values)

            except IndexError:
                pass

    # Ganglinien
    tsc = Visum.Net.TimeSeriesCont.GetAll
    names = [t.AttValue('Name') for t in tsc]

    if not v+'Tagesgang' in names:
        # create Ganglinie OVTagesgang
        no = free_gang.pop()
        cont = Visum.Net.TimeSeriesCont
        dt = 2  # DomainType = MatrixGanglinie
        ats = Visum.Net.AddTimeSeries(no,dt)  # Probleme bei Parameterübergabe
        ats.SetAttValue('Name', v+'Tagesgang')

        matrices = Visum.Net.Matrices.GetAll

        # Matrizen Zeitscheiben zuweisen
        for z, code in enumerate(zeit):
            von = int(code[:2])
            bis = int(code[2:])
            start = von * 60 * 60
            end = bis * 60 * 60 -1

            for m in matrices:
                m_code = m.AttValue('Code')
                if m_code == v+code:
                    m_no = m.AttValue('No')
                    a1 = ats.AddTimeSeriesItem(start, end)
                    a1.SetAttValue('Value', m_no)


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

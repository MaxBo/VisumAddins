# -*- coding: utf8 -*-
#------------------------------------------------------------------------------
# Name:        VISUM Matrices to HDF5 for each time
# Purpose:     Berechnet ÖV Kenngrößen nach vordefiniertem Verfahrem und Zeitscheiben
#              Speichert alle Kenngrößenmatrizen je berechneter Zeitscheibe in HDF5 Datei
#              -> nicht berechnete Matrizen erhalten in jeder Zeitscheibe den zuvor berechneten Wert
#
# Author:      Nina Kohnen
#
# Created:     03.04.2013
# Copyright:   (c) Barcelona 2013
# Licence:     <your licence>
#------------------------------------------------------------------------------


if __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from helpers.get_folders import get_folders
from helpers.get_params import get_params_from_visum
from helpers.latinize import latinize

import numpy
import tables
import VisumPy
import os
import sys
import time
from latinze import latinize
import VisumPy.AddIn

from VisumPy.helpers import GetMatrix, SetMatrix
from tables.exceptions import NoSuchNodeError

# Zeitschiebe aus GUI
class AddTimeSlices(object):
    def __init__(self):
        self.scenario_name = Visum.Net.AttValue('ScenarioCode')
        self.params = get_params_from_visum(Visum,
                                            self.scenario_name,
                                            ['OV'])
        self.export_arrays()

        self.visum2hdf_matrix_names = {
            'Fahrtweite-VSys(AST)': 'in_vehicle_distance_ast',
            'Fahrtweite-VSys(Bus)': 'in_vehicle_distance_bus',
            'Fahrzeit im Fahrzeug-VSys(AST)': 'in_vehicle_time_ast',
            'Fahrzeit im Fahrzeug-VSys(Bus)': 'in_vehicle_time_bus',
            'Fahrtweite': 'Fahrweite',
            'Gehzeit': 'Umsteigegehzeit',
            'Fahrzeit im Fahrzeug': 'FahrzeitimFahrzeug',
        }

    def export_arrays():
        """Export Array """
        AllMatrices = Visum.Net.Matrices.GetAll
        item = Visum.Net.AttValue('CURRENT_TIME_INTERVAL')

         # Open File
        with tables.openFile(filepath, 'a') as h:

            #Alle Matrizen
            for m in AllMatrices:

                m_type = m.AttValue('MatrixType')

                #Wenn Kenngroessenmatrix
                if m_type == 'MATRIXTYPE_SKIM':

                    #Create/Open HDF5
                    name = latinize(m.AttValue('Name'))
                    name = self.visum2hdf_matrix_names.get(name, name)
                    code = m.AttValue('Code')
                    no = m.AttValue('No')

                    root = h.root
                    #Matrix als Numpy array (hat funktion shape)
                    data = VisumPy.helpers.GetMatrix(Visum, no)

                    #Knoten visum?
                    try:
                        group = h.getNode(root, 'visum')
                    except NoSuchNodeError:
                        group = h.createGroup(root,'visum')
                    #addIn.ReportMessage(data)
                    try:
                        # Existiert der Knoten(Tabelle)
                        table_in_hdf5 = h.getNode(group, name)

                    except NoSuchNodeError:
                        # Wenn nicht :
                        m_shape = data.shape          # Get Shape
                        m_row = m_shape[0]             # Get Row Number
                        m_col = m_shape[1]              # Get Col Number
                        n_time_sclices = Visum.Net.AttValue('NUM_OF_TIMESLICES')

                        arr_shape = (n_time_sclices, m_row, m_col)


                        #Create Array (here)
                        arr = numpy.zeros(arr_shape, dtype='f4')

                        # create Table (in hdf5 file)
                        ##arrname = code+str(t)
                        table_in_hdf5 = h.createArray(group, name, arr)

                    # Fill table with Matrix

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
                zonetable.remove()
            except NoSuchNodeError:
                pass
            zones = Visum.Net.Zones
            nummer = numpy.array(VisumPy.helpers.GetMulti(zones, 'No'))
            name = numpy.array(VisumPy.helpers.GetMulti(zones, 'Name')).view(numpy.chararray).encode('cp1252')
            rec = numpy.rec.fromarrays([nummer, name],
                                       names=['zone_no',
                                      'zone_name'],
                                       titles=['Bezirke', 'BezirksNamen'],
                                       formats=['<i4', 'S255'])
            zonetable = h.createTable(h.root, 'Bezirke', rec)

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

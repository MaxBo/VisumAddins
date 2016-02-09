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

import numpy
import tables
import os
import sys
import subprocess
from argparse import ArgumentParser
import tempfile


#from VisumPy.helpers import GetMatrix, SetMatrix
from tables.exceptions import NoSuchNodeError

from get_params import get_params, get_params_from_visum, get_folders

i = []
# Zeitschiebe aus GUI


class CalcMatrix(object):

    mode = 'OV'

    def __init__(self):
        self.scenario_name = Visum.Net.AttValue('ScenarioCode')
        params = get_params_from_visum(Visum,
                                       self.scenario_name,
                                       ('Params', self.mode))
        self.h5_file = params[self.mode]
        self.h5_params_file = params['Params']
        self.time_series = []
        pythonpath, project_folder = get_folders(Visum)
        self.pythonpath = pythonpath
        self.project_folder = project_folder

    def calc(self):
        """calculate the skim matrices by looping over the time intervals"""
        # Get start/end Time from Analysezeiträume
        f = Visum.Procedures.Functions
        at = f.AnalysisTimes
        # Get Operation "Kenngrößenmatrix berechnen"
        # insert xml-file at first position
        path = os.path.dirname(__file__)
        xml = os.path.join(path,'ov_kgmatrix_operation.xml')
        ReadOperations_Insert = 2
        pos = 1
        Visum.Procedures.OpenXmlWithOptions(xml,
                                            readOperations=True,
                                            readFunctions=False,
                                            roType=ReadOperations_Insert)
        try:

            operations = Visum.Procedures.Operations

            op = operations.ItemByKey(pos)
            # loop over analysis times
            for t, ti in self.time_series:
                # set start end endtime from time intervales
                a = at.TimeInterval(t + 1)  # auswahl Zeitintervall
                start = a.AttValue('StartTime')
                end = a.AttValue('EndTime')
                put_ckmp = op.PuTCalcSkimMatrixParameters
                ttp = put_ckmp.TimetableBasedParameters
                ttbp = ttp.BaseParameters
                ttbp.SetTimeIntervalStart(start)  # Time in seconds
                ttbp.SetTimeIntervalEnd(end)    # Time in Seconds

                #setcurrentOperation
                Visum.Procedures.OperationExecutor.SetCurrentOperation(pos)
                Visum.Procedures.OperationExecutor.ExecuteCurrentOperation()
                self.store(t, ts)
        finally:
            # finally remove the inserted operation KG-Matrix-Berechnen
            operations.RemoveOperation(pos)

    def store(self, t, ts):
        """store skim matrix for time series ts to file"""
        """SCHREIBEN"""
        # Open File
        with tables.openFile(self.h5_file, 'a') as h:

            #Alle Matrizen
            AllMatrices = Visum.Net.Matrices.GetAll

            for m in AllMatrices:

                m_type = m.AttValue('MatrixType')

                #Wenn Kenngroessenmatrix
                if m_type == 'MATRIXTYPE_SKIM':

                    #Create/Open HDF5
                    name = latinize(m.AttValue('Name'))
                    name_dict = {
                        'Fahrtweite-VSys(AST)': 'in_vehicle_distance_ast',
                        'Fahrtweite-VSys(Bus)': 'in_vehicle_distance_bus',
                        'Fahrzeit im Fahrzeug-VSys(AST)': 'in_vehicle_time_ast',
                        'Fahrzeit im Fahrzeug-VSys(Bus)': 'in_vehicle_time_bus',
                        'Fahrtweite': 'Fahrweite',
                        'Gehzeit': 'Umsteigegehzeit',
                        'Fahrzeit im Fahrzeug': 'FahrzeitimFahrzeug',
                    }
                    table_name = name_dict.get(name, name)
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
                        table_in_hdf5 = h.getNode(group, table_name)

                    except NoSuchNodeError:
                        # Wenn nicht :
                        m_shape = data.shape          # Get Shape
                        m_row = m_shape[0]             # Get Row Number
                        m_col = m_shape[1]              # Get Col Number
                        zeit = len(self.time_series)

                        arr_shape = (zeit, m_row, m_col)

                        #Create Array (here)
                        arr = numpy.zeros(arr_shape, dtype='f4')

                        # create Table (in hdf5 file)
                        table_in_hdf5 = h.createArray(group, table_name, arr)

                        table_in_hdf5[t] = data

                    #Meta Infos (Node)
                    table_in_hdf5.attrs['Name'] = table_name
                    t = time.localtime()
                    date = time.asctime(t)
                    table_in_hdf5.attrs['Last Updated'] = date

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
            name = numpy.char.encode(VisumPy.helpers.GetMulti(zones, 'Name'),
                                     'cp1252')
            rec = numpy.rec.fromarrays([nummer, name],
                                       names=['zone_no',
                                      'zone_name'],
                                       titles=['Bezirke', 'BezirksNamen'],
                                       formats=['<i4', 'S255'])
            zonetable = h.createTable(h.root, 'Bezirke', rec)

            h.flush()


if __name__ == '__main__':
    parser = ArgumentParser(description="Parameter Importer")

    parser.add_argument("-f", action="store",
                        help="Projektordner mit XML-Projektdatei",
                        dest="project_folder", default=None)

    parser.add_argument("-s", action="store",
                        help="angegebenes Szenario ausführen",
                        dest="scenario_name", default=None)

    parser.add_argument("--pythonpath", action="store",
                      help="angegebenes Szenario ausführen",
                      dest="pythonpath", default='python')

    options = parser.parse_args()

##    calcMatrix = CalcMatrix.fromProjectFile(options.project_folder,
##                                            options.scenario_name,
##                                            options.pythonpath)
    calcMatrix = CalcMatrix()
    calcMatrix.import_time_series()
    #calcMatrix.calc()


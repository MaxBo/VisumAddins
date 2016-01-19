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
from collections import OrderedDict
from pprint import pprint
from decoder import Dict2XML
import tempfile
import latinze


#from VisumPy.helpers import GetMatrix, SetMatrix
from tables.exceptions import NoSuchNodeError

from get_params import get_params, get_params_from_visum

i = []
# Zeitschiebe aus GUI


class CalcMatrix(object):

    mode = 'OV'

    @classmethod
    def fromProjectFile(cls, project_folder, scenario_name, pythonpath):
        self = cls.__new__(CalcMatrix)
        self.scenario_name = scenario_name
        params = get_params(project_folder, scenario_name,
                            params=[self.mode, 'Params'],
                            pythonpath=pythonpath)
        self.h5_file = params[self.mode]
        self.h5_params_file = params['Params']
        self.time_series = []
        return self

    def __init__(self):
        self.scenario_name = Visum.Net.AttVal('ScenarioName')
        params = get_params_from_visum(Visum, scenario_name)
        self.h5_file = params[self.mode]
        self.h5_params_file = params['Params']
        self.time_series = []

    def import_time_series(self):
        with tables.openFile(self.h5_params_file) as h:
            try:
                time_series = h.root.activities.time_series[:]
            except NoSuchNodeError:
                msg = 'No table activities.time_series defined in {}'
                raise NoSuchNodeError(msg.format(self.h5_params_file))
            if not len(time_series):
                msg = 'table activities.time_series in {} is empty'
                raise ValueError(msg.format(self.h5_params_file))
        self.add_xml(time_series)

    def add_xml(self, time_series):
        """create time interval xml and import into Visum"""
        time_intervals = []
        d = {'@PROCEDURES': {'VERSION': '7'},
             'PROCEDURES': {'FUNCTIONS': {
                 '@ANALYSISTIMES': {'ENDDAYINDEX': '1',
                                    'STARTDAYINDEX': '1',
                                    'USEONPRTRESULTS': '1',
                                    'USEONPUTRESULTS': '1'},
                 'ANALYSISTIMEINTERVAL': time_intervals, }
             }}
        codes = []
        for t, ts in enumerate(time_series):
            ti = self.add_time_interval(ts['from_hour'],
                                        ts['to_hour'],
                                        codes,
                                        code=ts['code'])

            time_intervals.append(ti)
        aggr_ti = self.add_time_interval(time_series[0]['from_hour'],
                                         time_series[-1]['to_hour'],
                                         codes,
                                         is_aggregate=True)
        time_intervals.append(aggr_ti)

        pprint(d)
        # write xml to tempfile
        x = Dict2XML().parse(d)
        temp_path = tempfile.mktemp(suffix='xml')
        with open(temp_path, mode='w') as t:
            t.write(x)
        # and import to Visum
        ReadOperations_ReplaceAll = 0
        Visum.Procedures.OpenXmlWithOptions(temp_path,
                                            readOperations=False,
                                            readFunctions=True,
                                            roType=ReadOperations_ReplaceAll)


    def add_time_interval(self, starttime, endtime, codes, is_aggregate=False):
        """
        create xml-code for time interval

        Parameters
        ----------
        starttime : int
        endtime : int
        codes : list
        is_aggregate : bool (optional, default=False)
        code : str, optional
            if not given, it will be derived from the start- and endtime
        """
        code = '{st:02d}{et:02d}'.format(st=starttime, et=endtime)
        name = '{st:02d}h-{et:02d}h'.format(st=starttime, et=endtime)
        et = '{et:02d}:59:59'.format(et=endtime - 1)
        st = '{st:02d}:00:00'.format(st=starttime)
        if is_aggregate:
            ISAGGREGATE = '1'
            DERIVEDFROM = ','.join(codes)
            AGGRFUNCTION = 'SUM'

        else:
            ISAGGREGATE = '0'
            DERIVEDFROM = ''
            AGGRFUNCTION = 'MEAN'


        ti = {'#ANALYSISTIMEINTERVAL':
              {'AGGRFUNCTION': AGGRFUNCTION,
               'CODE': code,
               'DERIVEDFROM': DERIVEDFROM,
               'ENDDAYINDEX': '1',
               'ENDTIME': et,
               'ISAGGREGATE': ISAGGREGATE,
               'NAME': name,
               'STARTDAYINDEX': '1',
               'STARTTIME': st,
               }}

        if not is_aggregate:
            codes.append(code)
        return ti

    def remove_time_series(self):
        """remove all time series"""

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
"

def Run(param):

    #File Path from MatrixToHDF5Dlg
    filepath = param['filepath']

    """ZEITSCHEIBEN"""
    #Addin Path (Com Doku P.62)
    verzeichnis = 65
    path = Visum.GetPath(verzeichnis)
    path_name = str(path)
    ##addIn.ReportMessage(path)
    #Set Zeitscheiben - (COM Docu:99)
    Visum.Procedures.OpenXmlWithOptions(path+'zeitscheiben_addin.xml', 0,1)
    #Import Operation ÖV- (COM Docu:99)
    if param["OVIV"]== "OV": #OperationType 102
        Visum.Procedures.OpenXmlWithOptions(path+'ov_kassel.xml', 1,0,2)
    if param["OVIV"]== "IV": #OperationType 103
            Visum.Procedures.OpenXmlWithOptions(path+'iv_kassel.xml', 1,0,2)
    """BRECHNENEN"""
    # For each i:
    for item in i:
        #Get start/end Time from Analysezeiträume
        f = Visum.Procedures.Functions
        at = f.AnalysisTimes
        a = at.TimeInterval(item + 1)  # auswahl Zeitintervall
        start = a.AttValue('StartTime')
        end = a.AttValue('EndTime')
        if item == 4:
            end = 3600*24-1
        if item == 5:
            start = 0
            end = 3600*24-1

        #Get Operation
        operations = Visum.Procedures.Operations
        op = operations.ItemByKey(1)

        # Set Parameters ->In Tabelle auf S. 113/114 nachschauen
        if param["OVIV"]== "OV":
            put_ckmp = op.PuTCalcSkimMatrixParameters
            ttp = put_ckmp.TimetableBasedParameters
            ttbp = ttp.BaseParameters
            ttbp.SetTimeIntervalStart(start)  # Time in seconds
            ttbp.SetTimeIntervalEnd(end)    # Time in Seconds

        #setcurrentOperation
        Visum.Procedures.OperationExecutor.SetCurrentOperation(1)
        Visum.Procedures.OperationExecutor.ExecuteCurrentOperation()

        """SCHREIBEN"""
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
                    if name == 'Fahrtweite-VSys(AST)':
                        name = 'in_vehicle_distance_ast'
                    if name == 'Fahrtweite-VSys(Bus)':
                        name = 'in_vehicle_distance_bus'
                    if name == 'Fahrzeit im Fahrzeug-VSys(AST)':
                        name = 'in_vehicle_time_ast'
                    if name == 'Fahrzeit im Fahrzeug-VSys(Bus)':
                        name = 'in_vehicle_time_bus'
                    if name == 'Fahrtweite':
                        name = 'Fahrweite'
                    if name == 'Gehzeit':
                        name = 'Umsteigegehzeit'
                    if name == 'Fahrzeit im Fahrzeug':
                        name = 'FahrzeitimFahrzeug'
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
                        zeit = 5
                        # if 24 h
                        if item == 5:
                            zeit = 1

                        if param["OVIV"]== "OV":
                            arr_shape = (zeit, m_row, m_col)

                        if param["OVIV"]== "IV":
                            arr_shape = (m_row, m_col)


                        #Create Array (here)
                        arr = numpy.zeros(arr_shape, dtype='f4')

                        # create Table (in hdf5 file)
                        ##arrname = code+str(t)
                        table_in_hdf5 = h.createArray(group, name, arr)

                    # Fill table with Matrix
                    if param["OVIV"]== "IV":
                        table_in_hdf5[:] = data

                    elif item == 5:
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
    # Remove Operation again
    operations.RemoveOperation(1)


def main():
    calcMatrix = CalcMatrix()
    calcMatrix.import_time_series()
    for ts in calcMatrix.time_series:
        calcMatrix.calc(ts)
        calcMatrix.store(ts)
    calcMatrix.removeOperation()


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

    calcMatrix = CalcMatrix.fromProjectFile(options.project_folder,
                                            options.scenario_name,
                                            options.pythonpath)
    calcMatrix.import_time_series()
    calcMatrix.calc()


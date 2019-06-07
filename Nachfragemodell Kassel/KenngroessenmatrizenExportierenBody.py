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
from tables.exceptions import NoSuchNodeError
import VisumPy
import os
import sys
import time
import VisumPy.AddIn
from VisumPy.AddIn import AddIn, AddInState, AddInParameter

from VisumPy.helpers import GetMatrix, SetMatrix

class ExportSkims(object):

    visum2hdf_matrix_names = {
        'IVDT(AST)': 'in_vehicle_distance_ast',
        'IVDT(Bus)': 'in_vehicle_distance_bus',
        'IVTT(AST)': 'in_vehicle_time_ast',
        'IVTT(Bus)': 'in_vehicle_time_bus',
        'JRT': 'Reisezeit',
        'JRTA': 'Reisezeit angepasst',
        'RIT': 'Beförderungszeit',
        'RITA': 'Beförderungszeit angepasst',
        'IVT': 'FahrzeitimFahrzeug',
        'AXT': 'ÖV-Zusatz-Zeit',
        'OWT': 'Startwartezeit',
        'OWTA': 'Startwartezeit angepasst',
        'TWT': 'Umsteigewartezeit',
        'TWTA': 'Umsteigewartezeit angepasst',
        'XTWT': 'Erweiterte Umsteigewartezeit',
        'WOWT': 'Gewichtete Startwartezeit',
        'WTWT': 'Gewichtete Umsteigewartezeit',
        'WKT': 'Umsteigegehzeit',
        'ACT': 'Zugangszeit',
        'EGT': 'Abgangszeit',
        'PJT': 'Empfundene Reisezeit',
        'NTR': 'Umsteigehaufigkeit',
        'XIMP': 'Erweiterter Widerstand',
        'SFQ': 'Bedienungshaufigkeit',
        'DID': 'Luftlinienweite',
        'JRD': 'Reiseweite',
        'RID': 'Beförderungsweite',
        'IVD': 'Fahrweite',
        'AXD': 'ÖV-Zusatz-Weite',
        'WKD': 'Gehweite',
        'ACD': 'Zugangsweite',
        'EGD': 'Abgangsweite',
        'JRS': 'Reisegeschwindigkeit',
        'DIS': 'Luftliniengeschwindigkeit',
        'FAR': 'Fahrpreis',
        'NFZ': 'Anzahl Tarifzonen',
        'NOC': 'Anzahl Betreiberwechsel',
        'IVTD': 'Fahrtweite-VSys',
        'IVTP': 'Fahrtweite-VSys [%]',
        'IVTT': 'Fahrzeit im Fahrzeug-VSys',
        'IPD': 'Widerstand',
        'UTL': 'Nutzen',
        'PLA': 'Attribut für Teilweg-Kenngröße',
        'ADT': 'Anpassungszeit',
        'XADT': 'Erweiterte Anpassungszeit',
        'EJT': 'Reisezeitäquivalent',
        'DISC': 'Diskomfort durch Überlastung',
    }

    mode = 'OV'

    def __init__(self, Visum):
        self.Visum = Visum
        self.scenario_name = self.Visum.Net.AttValue('ScenarioCode')
        self.params = get_params_from_visum(Visum,
                                            self.scenario_name,
                                            [self.mode])

    def export_arrays(self):
        """Export Array """
        AllMatrices = self.Visum.Net.Matrices.GetAll
        item = int(self.Visum.Net.AttValue('CURRENT_TIME_INTERVAL'))
        filepath = self.params[self.mode]

        filters = tables.Filters(complevel=2, complib='blosc', shuffle=True)

         # Open File
        with tables.open_file(filepath, 'a', filters=filters) as h:

            #Alle Matrizen
            for m in AllMatrices:

                m_type = m.AttValue('MatrixType')

                #Wenn Kenngroessenmatrix
                if m_type == 'MATRIXTYPE_SKIM':

                    #Create/Open HDF5
                    name = latinize(m.AttValue('Name'))
                    code = m.AttValue('Code')
                    hdf5_name = self.visum2hdf_matrix_names.get(code, code)
                    no = int(m.AttValue('No'))

                    root = h.root
                    #Matrix als Numpy array (hat funktion shape)
                    data = VisumPy.helpers.GetMatrix(self.Visum, no)

                    #Knoten visum?
                    try:
                        group = h.get_node(root, 'visum')
                    except NoSuchNodeError:
                        group = h.create_group(root,'visum')
                    #addIn.ReportMessage(data)
                    try:
                        # Existiert der Knoten(Tabelle)
                        table_in_hdf5 = h.get_node(group, hdf5_name)

                    except NoSuchNodeError:
                        # Wenn nicht :
                        arr_shape = self.get_shape(data)


                        #Create Array (here)
                        arr = numpy.zeros(arr_shape, dtype='f4')

                        # create Table (in hdf5 file)
                        ##arrname = code+str(t)
                        table_in_hdf5 = h.create_array(group, hdf5_name, arr)

                    # Fill table with Matrix

                    self.set_values(item=item,
                                    data=data,
                                    table_in_hdf5=table_in_hdf5)

                    #Meta Infos (Node)
                    table_in_hdf5.attrs['Name'] = hdf5_name
                    t = time.localtime()
                    date = time.asctime(t)
                    table_in_hdf5.attrs['Last Updated'] = date

                    # Save
                    h.flush()

    def set_values(self, item, data, table_in_hdf5):
        table_in_hdf5[item] = data

    def get_shape(self, data):
        m_shape = data.shape          # Get Shape
        m_row = m_shape[0]             # Get Row Number
        m_col = m_shape[1]              # Get Col Number
        n_time_sclices = int(self.Visum.Net.AttValue('NUM_OF_TIMESLICES'))

        arr_shape = (n_time_sclices, m_row, m_col)
        return arr_shape



if __name__ == '__main__':
    export_skims = ExportSkims(Visum)
    export_skims.export_arrays()




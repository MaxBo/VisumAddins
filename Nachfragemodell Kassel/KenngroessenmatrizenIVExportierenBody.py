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
from KenngroessenmatrizenExportierenBody import ExportSkims


class ExportSkimsPrT(ExportSkims):

    visum2hdf_matrix_names = {
        'TT0': 't0',
        'TTC': 'tAkt',
        'DIS': 'Fahrweite',
    }

    mode = 'MIV'

    def get_shape(self, data):
        """MIV-Skims are only 2D"""
        m_shape = data.shape          # Get Shape
        m_row = m_shape[0]             # Get Row Number
        m_col = m_shape[1]              # Get Col Number
        arr_shape = (m_row, m_col)
        return arr_shape

    def set_values(self, data, table_in_hdf5, **kwargs):
        table_in_hdf5[:] = data


if __name__ == '__main__':
    export_skims = ExportSkimsPrT(Visum)
    export_skims.export_arrays()




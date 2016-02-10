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
from helpers.expand_array import expand_array

import numpy
import tables
from tables.exceptions import NoSuchNodeError
import VisumPy
import os
import sys
import time
import VisumPy.AddIn
from VisumPy.AddIn import AddIn, AddInState, AddInParameter
from VisumPy.helpers import GetMatrix, SetMatrix, GetMulti, __getMatrixByCode as getMatrixByCode
from VisumPy.matrices import fromNumArray

class ImportDemandMatrices(object):

    def __init__(self, Visum):
        self.Visum = Visum
        self.scenario_name = self.Visum.Net.AttValue('ScenarioCode')
        self.run_name = self.Visum.Net.AttValue('RunCode')
        run_name = '"{}"'.format(self.run_name)
        self.params = get_params_from_visum(Visum,
                                            self.scenario_name,
                                            [run_name])
        self.filepath = self.params[run_name]

    def import_arrays(self, mode, tablename):
        """Import Array """
        # Free Matrix NO
        matrices = self.Visum.Net.Matrices.GetAll
        all_numbers = set(range(1, 255))
        used_numbers = set([int(mat.AttValue('No')) for mat in matrices])
        free_matrix_no = all_numbers.difference(used_numbers)

        # Free Ganglinien NO
        gang = self.Visum.Net.TimeSeriesCont.GetAll
        all_gang = set(range(1, 25))
        used_gang = set([int(g.AttValue('No')) for g in gang])
        free_gang = all_gang.difference(used_gang)

        f = self.Visum.Procedures.Functions
        at = f.AnalysisTimes

        time_intervals = []
        aggregate = []

        for t in xrange(at.NumTimeIntervals):
            ti = at.TimeInterval(t + 1)
            time_intervals.append(ti)

        codes = GetMulti(self.Visum.Net.Matrices, 'Code')

        zones_visum = self.Visum.Net.Zones.GetAll
        zones_no_visum = numpy.array(GetMulti(self.Visum.Net.Zones,
                                              'No')).astype('i4')

        # Does Matrix exist?
        for z, ti in enumerate(time_intervals):
            code = ti.AttValue('Code')
            #ovcode = 'OV%s' %code.encode("iso-8859-15")
            ovcode = '{m}_{ti}'.format(m=mode,
                                       ti=code.encode("iso-8859-15"))
            if not ovcode in codes:
                # add Matrix
                no = free_matrix_no.pop()
                a = self.Visum.Net.AddMatrix(no)

                # Set DemandMatrix parameters
                a.SetAttValue('Name', ovcode)
                a.SetAttValue('Code', ovcode)
                a.SetAttValue('MatrixType', 'MATRIXTYPE_DEMAND')

            # Fill Matrix
            with tables.openFile(self.filepath, 'r') as h:
                # zone definition in the hdf5-file
                zones_in_hdf5 = h.getNode(h.root, 'zones')
                zones_h5 = zones_in_hdf5.col('zone_no')
                try:
                    if not ti.AttValue('IsAggregate'):
                        if tablename != 'all':
                            table_in_hdf5 = h.getNode(h.root.modes_ts, tablename)
                            tt = table_in_hdf5[z]
                        else:
                            tt = 0
                            ts = h.root.modes_ts
                            for table_in_hdf5 in ts:
                                tt += table_in_hdf5[z]

                    # für aggregate 24h
                    else:
                        if tablename != 'all':
                            table_in_hdf5 = h.getNode(h.root.modes, tablename)
                            tt = table_in_hdf5[:]
                        else:
                            tt = 0
                            all_trips = h.root.modes
                            for table_in_hdf5 in all_trips:
                                tt += table_in_hdf5[:]


                    # expand array to VISUM zone definition
                    tt_expanded = expand_array(arr=tt,
                                               arr_zones=zones_h5,
                                               zone_no=zones_no_visum,
                                               fill_value=0)
                    # set Matrix
                    f = fromNumArray(tt_expanded, zones_visum)
                    values = f['datavalues']
                    SetMatrix(self.Visum, ovcode, values)

                except IndexError:
                    pass



        # Ganglinien
        tsc = self.Visum.Net.TimeSeriesCont.GetAll
        names = [t.AttValue('Name') for t in tsc]

        ganglinien_name = mode + 'Tagesgang'
        if not ganglinien_name in names:
            # create Ganglinie OVTagesgang
            no = free_gang.pop()
            cont = self.Visum.Net.TimeSeriesCont
            DomainTypeMatrices = 1  # DomainType = MatrixGanglinie
            ats = self.Visum.Net.AddTimeSeries(no, DomainTypeMatrices)
            ats.SetAttValue('Name', ganglinien_name)
        else:
            # remove existing TimeSeriesItems
            for ts in tsc:
                if ts.AttValue('Name') == ganglinien_name:
                    for a in ts.TimeSeriesItems:
                        ts.RemoveTimeSeriesItem(a)
                    ats = ts


        matrices = self.Visum.Net.Matrices.GetAll

        # Matrizen Zeitscheiben zuweisen
        for z, ti in enumerate(time_intervals):
            is_aggregate = ti.AttValue('IsAggregate')
            valid_ti = self.is_valid_ti(is_aggregate)
            if valid_ti:
                code = ti.AttValue('Code')
                name = ti.AttValue('Name')
                von = int(name[:2])
                bis = int(name[4:6])
                start = von * 60 * 60
                end = bis * 60 * 60 -1
                ovcode = '{m}_{ti}'.format(m=mode,
                                           ti=code.encode("iso-8859-15"))

                m = getMatrixByCode(self.Visum, ovcode)
                if m is not None:
                    m_no = int(m.AttValue('No'))
                    a1 = ats.AddTimeSeriesItem(start, end)
                    matrix_name = 'Matrix({})'.format(m_no)
                    a1.SetAttValue('Matrix', matrix_name)

    def is_valid_ti(self, is_aggregate):
        """Check if aggregate time intervals should be used or not"""
        return not is_aggregate


if __name__ == '__main__':
    import_matrices = ImportDemandMatrices(Visum)
    import_matrices.import_arrays(mode='put', tablename='put')




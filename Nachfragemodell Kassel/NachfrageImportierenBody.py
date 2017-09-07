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
import tempfile
temp_logfile = tempfile.mktemp(suffix="log")

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

    def get_time_series(self, mode):
        """get the time series"""
        ts_name = '{}Tagesgang'.format(mode)

        at = self.Visum.Procedures.Functions.AnalysisTimes
        time_intervals = []
        aggregate = []

        for t in xrange(at.NumTimeIntervals):
            ti = at.TimeInterval(t + 1)
            time_intervals.append(ti)


        DomainTypeMatrices = 1

        tsc = self.Visum.Net.TimeSeriesCont
        it = tsc.Iterator
        it.Reset()
        found = False
        while it.Valid:
            ts = it.Item
            ts_no = ts.AttValue('No')
            if ts.AttValue('Name') == ts_name:
                found = True
                break
            it.Next()
        if not found:
            ts_no += 1

            ts = self.Visum.Net.AddTimeSeries(No=ts_no,
                                              domainType=DomainTypeMatrices)
        tsits = ts.TimeSeriesItems.GetAll
        for tsi in tsits:
            ts.RemoveTimeSeriesItem(tsi)
        return tsits

    def import_arrays(self, mode, tablename):
        """Import Array """
        #tsits = self.get_time_series(mode)
        # Free Matrix NO
        with open(temp_logfile, 'w') as fi:

            matrices = self.Visum.Net.Matrices.GetAll
            all_numbers = set(range(1, 255))
            used_numbers = set([int(mat.AttValue('No')) for mat in matrices])
            free_matrix_no = all_numbers.difference(used_numbers)

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
                self.import_matrix(ti, mode, codes,
                                   free_matrix_no, tablename,
                                   z, fi, zones_no_visum,
                                   zones_visum)

            ats, dts = self.add_ganglinien(fi, mode)
            matrices = self.Visum.Net.Matrices.GetAll

            # Matrizen Zeitscheiben zuweisen
            for z, ti in enumerate(time_intervals):
                self.assign_time_itervals(ti, mode, ats)

            # Gesamtnachfrage der Personengruppe zuweisen
            dsegs = {'put': u'ÖV',
                    'car': 'PKW_PRIV'}
            dseg_name = dsegs[mode]
            it = self.Visum.Net.DemandSegments.Iterator
            found = False
            while it.Valid:
                dseg = it.Item
                dseg_code = dseg.AttValue('Code')
                if dseg.AttValue('Name') == dseg_name:
                    found = True
                    break
                it.Next()
            if not found:
                raise AttributeError(
                    'demand segment {} does not exists'.format(dseg_name))
            dd=dseg.getDemandDescription()

            found = False
            for ti in time_intervals:
                if ti.AttValue('IsAggregate'):
                    code = ti.AttValue('Code')
                    name = ti.AttValue('Name')
                    von = int(name[:2])
                    bis = int(name[4:6])
                    start = von * 60 * 60
                    end = bis * 60 * 60 -1
                    ovcode = '{m}_{ti}'.format(m=mode,
                                               ti=code.encode("iso-8859-15"))

                    m = getMatrixByCode(self.Visum, ovcode)
                    found = True
            if not found:
                raise ValueError('No aggregate Matrix found')
            matrix_no = m.AttValue('No')
            dd.SetAttValue('Matrix', u'Matrix({:0.0f})'.format(matrix_no))
            dd.SetAttValue('DemandTimeSeriesNo', dts.AttValue('No'))


    def assign_time_itervals(self, ti, mode, ats):
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

    def add_ganglinien(self, fi, mode):
        # Free Ganglinien NO
        gang = self.Visum.Net.TimeSeriesCont.GetAll
        gang_names = [g.AttValue('Name') for g in gang]

        # Ganglinien
        fi.writelines('{}'.format(gang_names))

        ganglinien_name = mode + 'Tagesgang'
        if not ganglinien_name in gang_names:
            # create Ganglinie OVTagesgang
            all_gang = set(range(1, 255))
            used_gang = set([int(g.AttValue('No')) for g in gang])
            free_gang = all_gang.difference(used_gang)
            no = free_gang.pop()
            cont = self.Visum.Net.TimeSeriesCont
            DomainTypeMatrices = 1  # DomainType = MatrixGanglinie
            ats = self.Visum.Net.AddTimeSeries(no, DomainTypeMatrices)
            ats.SetAttValue('Name', ganglinien_name)
        else:
            # remove existing TimeSeriesItems
            tsc = self.Visum.Net.TimeSeriesCont
            for ts in tsc:
                if ts.AttValue('Name') == ganglinien_name:
                    for a in ts.TimeSeriesItems:
                        ts.RemoveTimeSeriesItem(a)
                    ats = ts

        # add DemandTimeSeries
        cont = self.Visum.Net.DemandTimeSeriesCont
        found = False
        it = cont.Iterator
        it.Reset()
        while it.Valid:
            dts = it.Item
            if dts.AttValue('Name') == ganglinien_name:
                found = True
                # assign TimeSeries
                dts.SetAttValue('TimeSeriesNo', ats.AttValue('No'))
                break
            it.Next()

        if not found:
            # create Demand Time Series
            # create Ganglinie OVTagesgang
            all_gang = set(range(1, 255))
            used_gang = set([int(g.AttValue('No')) for g in cont])
            free_gang = all_gang.difference(used_gang)
            no = free_gang.pop()
            DomainTypeMatrices = 1  # DomainType = MatrixGanglinie
            dts = self.Visum.Net.AddDemandTimeSeries(no, ats.AttValue('No'))
            dts.SetAttValue('Name', ganglinien_name)
            dts.SetAttValue('Code', ganglinien_name)

        return ats, dts

    def import_matrix(self, ti, mode, codes, free_matrix_no, tablename, z, fi, zones_no_visum, zones_visum):
        code = ti.AttValue('Code')
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
        with tables.open_file(self.filepath, 'r') as h:
            # zone definition in the hdf5-file
            zones_in_hdf5 = h.get_node(h.root, 'zones')
            zones_h5 = zones_in_hdf5.col('zone_no')
            try:
                if not ti.AttValue('IsAggregate'):
                    if tablename != 'all':
                        table_in_hdf5 = h.get_node(h.root.modes_ts, tablename)
                        tt = table_in_hdf5[z]
                        fi.writelines('{}'.format(z))
                    else:
                        tt = 0
                        ts = h.root.modes_ts
                        for table_in_hdf5 in ts:
                            tt += table_in_hdf5[z]
                        fi.writelines('{}'.format(z))

                # für aggregate 24h
                else:
                    if tablename != 'all':
                        table_in_hdf5 = h.get_node(h.root.modes, tablename)
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
                fi.writelines('{}'.format('matrix_set'))

            except IndexError:
                pass

    def is_valid_ti(self, is_aggregate):
        """Check if aggregate time intervals should be used or not"""
        return not is_aggregate


if __name__ == '__main__':
    import_matrices = ImportDemandMatrices(Visum)
    import_matrices.import_arrays(mode='put', tablename='put')




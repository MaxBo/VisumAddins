# -*- coding: utf-8 -*-

import numpy as np
from argparse import ArgumentParser


def main(generation, destmode):
    """"""
    aggregate_home_trips_to_dm_groups(generation, destmode)

def aggregate_home_trips_to_dm_groups(dm_name1='VisemGeneration',
                                      dm_name2='VisemT'):
    """"""
    dm1 = Visum.Net.DemandModels.ItemByKey(dm_name1)
    dm2 = Visum.Net.DemandModels.ItemByKey(dm_name2)
    zones = Visum.Net.Zones
    dsts = dm1.DemandStrata
    ds_codes = np.rec.fromrecords(dsts.GetMultipleAttributes(['code',
                                                              'DS_ModeDest']),
                            names=['code', 'DS_ModeDest'])

    attrs = ['HomeTrips({})'.format(d[0]) for d in ds_codes]
    ra = np.rec.fromrecords(zones.GetMultipleAttributes(attrs), names=attrs)

    dsts2 = dm2.DemandStrata
    ds2_codes = np.rec.fromrecords(dsts2.GetMultipleAttributes(['code']),
                                   names=['code'])

    attrs2 = ['HomeTrips({})'.format(d[0]) for d in ds2_codes]
    arr = np.zeros((zones.Count, dsts2.Count), dtype='f8')
    dt = np.dtype({'names': attrs2,
                   'formats': ['f8' for i in range(dsts2.Count)]})
    ra2 = arr.ravel().view(type=np.recarray, dtype=dt)
    for i, d in enumerate(ds_codes):
        detailed_column = 'HomeTrips({})'.format(d['code'])
        aggregated_column = 'HomeTrips({})'.format(d['DS_ModeDest'])
        ra2[aggregated_column] += ra[detailed_column]

    zones.SetMultipleAttributes(attrs2, ra2)


if __name__ == '__main__':

    argparse = ArgumentParser()
    argparse.add_argument('-g', help='name of the generation model',
                          dest='generation', default='VisemGeneration')
    argparse.add_argument('-d', help='name of the Destination-Modechoice model',
                          dest='destmode', default='VisemT')
    options = argparse.parse_args()
    main(options.generation, options.destmode)
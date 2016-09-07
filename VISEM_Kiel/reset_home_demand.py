# -*- coding: utf-8 -*-

import numpy as np
from argparse import ArgumentParser


def main(generation, destmode):
    """"""
    reset_demand(generation)

def reset_demand(dm_name1='VisemGeneration'):
    """Reset demand to 0 for Groups generation"""
    dm1 = Visum.Net.DemandModels.ItemByKey(dm_name1)
    zones = Visum.Net.Zones
    dsts = dm1.DemandStrata
    ds_codes = np.rec.fromrecords(dsts.GetMultipleAttributes(['code',
                                                              'DS_ModeDest']),
                            names=['code', 'DS_ModeDest'])
    attrs = ['HomeTrips({})'.format(d[0]) for d in ds_codes]
    ra = np.rec.fromrecords(zones.GetMultipleAttributes(attrs), names=attrs)
    ra[:] = 0
    zones.SetMultipleAttributes(attrs, ra)

if __name__ == '__main__':

    argparse = ArgumentParser()
    argparse.add_argument('-g', help='name of the generation model',
                          dest='generation', default='VisemGeneration')
    argparse.add_argument('-d', help='name of the Destination-Modechoice model',
                          dest='destmode', default='VisemT')
    options = argparse.parse_args()
    main(options.generation, options.destmode)
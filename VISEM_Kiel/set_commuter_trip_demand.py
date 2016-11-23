# -*- coding: utf-8 -*-

import numpy as np
import os
from argparse import ArgumentParser


def main(options):
    """"""
    fn = os.path.join(options.folder, options.filename)   
    set_commuter_trip_generation(options.destmode, fn)


def set_commuter_trip_generation(dm_name, fn):
    """
    Go through the rows of the given csv-file located in 
    folder\filename and
    Get HomeDemand for that group
    recalculate the HomeDemand for Groups in column `demandstratumnew`
    as value from `demandstratumold` * factor
    Write back the recalculated Home-Demand
    """

    factors = np.recfromcsv(open(fn, 'rb'), delimiter=';',
                            dtype=('U50','U50','f8'))
    
    origin_ds = factors.demandstratumold
    target_ds = factors.demandstratumnew
    
    ds_codes = np.unique(np.concatenate((
        origin_ds, target_ds)))
    
    cols = ['code'] + ds_codes.tolist()
    
    attrs = ['code'] + ['HomeTrips({})'.format(d) for d in ds_codes]


    dm2 = Visum.Net.DemandModels.ItemByKey(dm_name)
    zones = Visum.Net.Zones
    dsts = dm2.DemandStrata
    
    ra = np.rec.fromrecords(zones.GetMultipleAttributes(attrs), names=cols)
    
    for row in factors:
        ra[row['demandstratumnew']] = ra[row['demandstratumold']] * row['factor']

    ra.dtype.names = attrs
    zones.SetMultipleAttributes(attrs, ra)


if __name__ == '__main__':

    argparse = ArgumentParser()
    argparse.add_argument('-d', help='name of the Destination-Modechoice model',
                          dest='destmode', default='VisemT')
    argparse.add_argument('-f', help='name of the Folder with the ',
                              dest='folder', 
                              default=r'C:\601 aktuelles Szenario\Kiel\SharedData')
    argparse.add_argument('-n', help='name of the Filename of the factor file',
                              dest='filename', 
                              default=r'Factors_Commuters.csv')
        
    options = argparse.parse_args()
    main(options)
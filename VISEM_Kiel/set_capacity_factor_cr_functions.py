# -*- coding: utf-8 -*-

from argparse import ArgumentParser


def main(Visum, capacityFactor):
    """"""
    crs = Visum.Procedures.Functions.CRFunctions
    
    for i in range(1, 100):
        cr = crs.CrFunction(i)
        cr.SetAttValue('capacityFactor', capacityFactor)
        


if __name__ == '__main__':
    argparse = ArgumentParser()
    argparse.add_argument('-f', help='CapacityFactor',
                          dest='capacityFactor', default=9.0)
    options = argparse.parse_args()
    main(Visum, options.capacityFactor)

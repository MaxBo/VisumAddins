# -*- coding: utf8 -*-
#-------------------------------------------------------------------------------
# Name:        ÖV-Matrizen vorberechnen
# Purpose:
#
# Author:      Max Bohnet
#-------------------------------------------------------------------------------

from PreprocessPuTMatricesCode import PreprocessPuTMatrices

if __name__ == '__main__':
    preprocess_put_matrices = PreprocessPuTMatrices(Visum)
    preprocess_put_matrices.export_zones()
    preprocess_put_matrices.execute()


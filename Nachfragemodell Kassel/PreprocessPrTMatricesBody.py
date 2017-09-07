# -*- coding: utf8 -*-
#-------------------------------------------------------------------------------
# Name:        ÖV-Matrizen vorberechnen
# Purpose:
#
# Author:      Max Bohnet
#-------------------------------------------------------------------------------

from PreprocessPuTMatricesCode import PreprocessMatrices


class PreprocessPrTMatrices(PreprocessMatrices):
    """Preprocess the Private Transport Matrices"""

    mode = 'MIV'
    preprocess_command = '--pp_prt'

if __name__ == '__main__':
    preprocess_matrices = PreprocessPrTMatrices(Visum)
    preprocess_matrices.export_zones()
    preprocess_matrices.execute()


# -*- coding: utf8 -*-
#-------------------------------------------------------------------------------
# Name:        ÖV-Matrizen vorberechnen
# Purpose:
#
# Author:      Max Bohnet
#-------------------------------------------------------------------------------

import PreprocessPuTMatricesCode
reload(PreprocessPuTMatricesCode)

from PreprocessPuTMatricesCode import PreprocessMatrices

class PreprocessPuTMatrices(PreprocessMatrices):
    """Preprocess the Public Transport Matrices"""

    mode = 'OV'
    preprocess_command = '--pp_put'

if __name__ == '__main__':
    preprocess_matrices = PreprocessPuTMatrices(Visum)
    preprocess_matrices.export_zones()
    preprocess_matrices.execute()


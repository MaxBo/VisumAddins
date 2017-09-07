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


from NachfrageImportierenBody import ImportDemandMatrices

class ImportPrTDemandMatrices(ImportDemandMatrices):

    def is_valid_ti(self, is_aggregate):
        """Check if aggregate time intervals should be used or not"""
        return is_aggregate

if __name__ == '__main__':
    import_matrices = ImportPrTDemandMatrices(Visum)
    import_matrices.import_arrays(mode='car', tablename='car')




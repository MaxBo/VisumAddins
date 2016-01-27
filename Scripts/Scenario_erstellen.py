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

import numpy
import tables
import os
import sys
import subprocess
from argparse import ArgumentParser
from pprint import pprint

from get_params import get_scenarios, get_scenarios_from_visum


class ValidateScerario(object):

    def __init__(self):
        self.scenarios = get_scenarios_from_visum(Visum)

    def validate_scenarios(self):
        scenario_name = Visum.Net.AttValue('ScenarioCode')
        if not scenario_name in self.scenarios:
            cmd = '{pythonpath} -m gui_vm.clone_scenario -o "{project_xml_file}" -t "{template}" -s "{new_scenario}"'





if __name__ == '__main__':
    pass

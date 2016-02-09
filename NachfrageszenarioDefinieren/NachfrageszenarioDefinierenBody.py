# -*- coding: utf8 -*-
#------------------------------------------------------------------------------
# Name:        NachfrageszenarioDefinieren
# Purpose:     Define Demand Scenarios
#
# Author:      Max Bohnet
#
#------------------------------------------------------------------------------
if __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from helpers.check_scenario import validate


if __name__ == '__main__':
    validate(Visum, use_scenario_from_net=False)


# -*- coding: utf8 -*-
#------------------------------------------------------------------------------
# Name:     validate_scenario
# NamePurpose: Select or validate given Scenario and write Attribute Net.ScenarioCode
#
# Author:      Max Bohnet
#
# Created:     03.04.2013
# Copyright:   (c) 2015
# Licence:     <your licence>
#------------------------------------------------------------------------------

from check_scenario import validate


if __name__ == '__main__':
    validate(Visum, use_scenario_from_net=False)
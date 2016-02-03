# -*- coding: utf8 -*-
#------------------------------------------------------------------------------
# Name:        DefineScenario
# Purpose:     erstelle Nachfrage-Szenario und ggf. Modifikation
#
# Author:      Max Bohnet
#
# Created:     20.01.2016
# Copyright:   (c) Barcelona 2013
# Licence:     <your licence>
#------------------------------------------------------------------------------

from get_params import validate_scenario_from_visum


def main():
    # take scenario_name from Net Attributes if defined
    scenario_name = Visum.Net.AttValue('ScenarioCode')
    # validate the Scenario_name or create a new one
    scenario_name = validate_scenario_from_visum(Visum)

    # create a Scenario Modification (or define a new one)
    project = Visum.ScenarioManagement.CurrentProject
    code = 'Scenario_{sc}'.format(sc=scenario_name)
    modification = get_modification_by_code(code)
    modification.SetAttValue('Group', 'ScenarioNames')
    # defnie the modification
    modification.StartEditModification()
    Visum.SetAttValue('ScenarioCode', scenario_name)
    modification.EndEditModification()
    # set it to incompatible to other modifications in group "ScenarioNames"
    for m in project.Modifications:
        if m.AttValue('Group') == 'ScenarioNames':
            modification.DoesNotOverlapWith(m.AttValue('No'))


def get_modification_by_code(project, code):
    """
    return a modification with a given code or create a new one, if not exists
    """
    modifications = project.Modifications
    for modification in modifications.Iterator():
        if modification.AttValue('Code') == code:
            return modification
    modification = project.AddModification()
    modification.SetAttValue('Code', code)
    return modification


if __name__ == '__main__':
    main()
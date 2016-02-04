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


def validate(Visum, use_scenario_from_net=True):
    try:
        project = Visum.ScenarioManagement.CurrentProject
    except:
        msg = 'You have to run this Script out of the Scenario-Management'
        raise RuntimeError(msg)

    # take scenario_name from Net Attributes if defined
    scenario_name = Visum.Net.AttValue('ScenarioCode')
    # validate the Scenario_name or create a new one
    scenario_name = validate_scenario_from_visum(Visum, use_scenario_from_net)

    # create a Scenario Modification (or define a new one)
    project = Visum.ScenarioManagement.CurrentProject
    code = 'DemandScenario_{sc}'.format(sc=scenario_name)
    modification = get_modification_by_code(project, code)
    modification.SetAttValue('Group', 'DemandScenarios')
    # defnie the modification
    modification.StartEditModification()
    Visum.Net.SetAttValue('ScenarioCode', scenario_name)
    modification.EndEditModification()
    # set it to incompatible to other modifications in group "ScenarioNames"
    exclusions = []
    for m in project.Modifications:
        if m.AttValue('Group') == u'DemandScenarios':
            m_no = m.AttValue('No')
            if m_no != modification.AttValue('No'):
                exclusions.append(str(m_no))
    modification.SetAttValue(u'Exclusion', u','.join(exclusions))


def get_modification_by_code(project, code):
    """
    return a modification with a given code or create a new one, if not exists
    """
    modifications = project.Modifications
    for modification in modifications:
        if modification.AttValue('Code') == code:
            return modification
    modification = project.AddModification()
    modification.SetAttValue('Code', code)
    return modification

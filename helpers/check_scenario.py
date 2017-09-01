# -*- coding: utf8 -*-
#------------------------------------------------------------------------------
# Name:        DefineScenario
# Purpose:     erstelle Nachfrage-Szenario und ggf. Modifikation
#
# Author:      Max Bohnet
#
# Created:     20.01.2016
#------------------------------------------------------------------------------

if __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import os
import helpers.wingdbstub
from helpers.get_params import validate_scenario_from_visum


def validate(Visum, use_scenario_from_net=True):
    try:
        project = Visum.ScenarioManagement.CurrentProject
    except:
        msg = 'You have to run this Script out of the Scenario-Management'
        raise RuntimeError(msg)

    # take scenario_name from Net Attributes if defined
    scenario_name = Visum.Net.AttValue('ScenarioCode')
    # validate the Scenario_name or create a new one
    scenario_name, run= validate_scenario_from_visum(Visum,
                                                     use_scenario_from_net)

    create_modifications(Visum, scenario_name, u'DemandScenarios',
                         u'ScenarioCode')
    create_modifications(Visum, run, u'DemandRuns', u'RunCode')

def create_modifications(Visum, scenario_name, group, net_attribute ):
    # create a Scenario Modification (or define a new one)
    project = Visum.ScenarioManagement.CurrentProject
    code = '{group}_{sc}'.format(group=group, sc=scenario_name)
    modification = get_modification_by_code(project, code)

    modification.SetAttValue('Group', group)
    # define the modification
    filetype_ModelTransfer = 71
    base_path = os.path.dirname(os.path.dirname(
        Visum.GetPath(filetype_ModelTransfer)))
    tra_file = os.path.join(base_path, 'Modifications',
                            modification.AttValue('TraFile'))
    with open(tra_file, 'w') as f:
        f.write('''$VISION
$VERSION:VERSNR;FILETYPE;LANGUAGE
10.000;Trans;DEU
$NETZ:{na}
{sn}
'''.format(na=net_attribute, sn=scenario_name))

    # set it to incompatible to other modifications in group "ScenarioNames"
    exclusions = []
    for m in project.Modifications:
        if m.AttValue('Group') == group:
            m_no = m.AttValue('No')
            if m_no != modification.AttValue('No'):
                exclusions.append('{:0.0f}'.format(m_no))
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

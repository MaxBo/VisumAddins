# -*- coding: utf8 -*-
#------------------------------------------------------------------------------
# Name:        Get Visum Files
# Purpose:     hole Parameter aus xml-Datei
#
#
#
# Author:      Max Bohnet
#
# Created:     03.04.2013
# Copyright:   (c) 2015
# Licence:     <your licence>
#------------------------------------------------------------------------------

import subprocess
import os
from argparse import ArgumentParser


def get_params(project_folder, scenario_name, params,
               pythonpath=r'python'):
    """
    get param values for params for scenario

    Parameters
    ----------
    project_folder : str
        path to the project folder

    scenario_name : str
        the scenario to check

    params : list of str
        the parameters to read

    pythonpath : str (optional, default='python')
        path of python executable

    Returns
    -------
    param_values : list of str
        the values for params in scenario
    """
    project_xml_file = os.path.join(project_folder, 'project.xml')
    params_to_read = ' '.join(('"{param}"'.format(param=param) for param in params))
    cmd = '{pythonpath} -m gui_vm.get_param_from_config -o "{project_xml_file}" -s "{scenario_name}" -p {params_to_read}'
    c = subprocess.Popen(cmd.format(pythonpath=pythonpath,
                                    project_xml_file=project_xml_file,
                                    scenario_name=scenario_name,
                                    params_to_read=params_to_read),
                         stdout=subprocess.PIPE, shell=True)

    param_values = {}
    for i, path in enumerate(c.stdout.readlines()):
        # .strip() löscht Zeilenenden
        param_values[params[i]] = path.strip()
    return param_values

def get_params_from_visum(Visum, scenario_name, params):
    """
    get param values for params for scenario

    Parameters
    ----------
    Visum : Visum-instance

    scenario_name : str
        the scenario to check

    params : list of str
        the parameters to read

    Returns
    -------
    param_values : list of str
        the values for params in scenario
    """
    filetype_OtherOutputData = 89
    pythonpath = os.path.join(str(Visum.GetPath(filetype_OtherOutputData)), 'python')

    filetype_OtherInputData = 88
    project_folder = str(Visum.GetPath(filetype_OtherInputData))

    res = get_params(project_folder=project_folder,
                     scenario_name=scenario_name,
                     params=params,
                     pythonpath=pythonpath)
    return res


def get_scenarios_from_visum(Visum):
    """
    get available scenarios

    Parameters
    ----------
    Visum : Visum-instance

    Returns
    -------
    scenarios : list of str
        the available scenarios
    """
    filetype_OtherOutputData = 89
    pythonpath = os.path.join(str(Visum.GetPath(filetype_OtherOutputData)), 'python')

    filetype_OtherInputData = 88
    project_folder = str(Visum.GetPath(filetype_OtherInputData))

    return get_scenarios(project_folder, pythonpath)


def get_scenarios(project_folder, pythonpath=r'python', **kwargs):
    """
    get available scenarios

    Parameters
    ----------
    project_folder : str
        path to the project folder

    pythonpath : str (optional, default='python')
        path of python executable
    Returns
    -------
    scenarios : list of str
        the available scenarios
    """
    project_xml_file = os.path.join(project_folder, 'project.xml')
    cmd = '{pythonpath} -m gui_vm.get_scenarios_from_config -o "{project_xml_file}"'
    c = subprocess.Popen(cmd.format(pythonpath=pythonpath,
                                    project_xml_file=project_xml_file),
                         stdout=subprocess.PIPE, shell=True)

    scenarios = []
    for i, scenario in enumerate(c.stdout.readlines()):
        # .strip() löscht Zeilenenden
        scenarios.append(scenario.strip())
    return scenarios


def clone_scenario(project_folder, pythonpath,
                   template, scenario_name):
    """
    clone scenario

    Parameters
    ----------
    project_folder : str

    pythonpath : str

    template : str

    scenario_name : str
    """
    project_xml_file = os.path.join(project_folder, 'project.xml')
    cmd = '{pythonpath} -m gui_vm.clone_scenario -o "{project_xml_file}" -t "{template}" -s "{new_scenario}"'
    c = subprocess.Popen(cmd.format(pythonpath=pythonpath,
                                    project_xml_file=project_xml_file,
                                    template=template,
                                    new_scenario=scenario_name),
                         stdout=subprocess.PIPE, shell=True)

    for i, scenario in enumerate(c.stdout.readlines()):
        print(i, scenario)


def clone_scenario_from_visum(Visum, template, scenario_name):
    """
    clone scenario

    Parameters
    ----------
    Visum : Visum-instance

    template : str

    scenario_name : str

    Returns
    -------
    scenarios : list of str
        the available scenarios
    """
    filetype_OtherOutputData = 89
    pythonpath = os.path.join(str(Visum.GetPath(filetype_OtherOutputData)), 'python')

    filetype_OtherInputData = 88
    project_folder = str(Visum.GetPath(filetype_OtherInputData))

    return clone_scenario(project_folder, pythonpath, template, scenario_name)


def validate_scenario(project_folder,
                      scenario_name,
                      pythonpath=r'python',
                      **kwargs):
    """
    validate available scenarios

    Parameters
    ----------
    project_folder : str
        path to the project folder
    scenario_name : str
        name of the scenario

    pythonpath : str (optional, default='python')
        path of python executable
    Returns
    -------
    scenarios : list of str
        the available scenarios
    """
    project_xml_file = os.path.join(project_folder, 'project.xml')
    cmd = '{pythonpath} -m gui_vm.validate_scenario -f "{project_xml_file}" -s {sc}'
    c = subprocess.Popen(cmd.format(pythonpath=pythonpath,
                                    project_xml_file=project_xml_file,
                                    sc=scenario_name),
                         stdout=subprocess.PIPE, shell=True)

    line = c.stdout.readline().strip()
    if line.startswith('selected scenario:'):
        scenario = line.split(':')[1]
    elif line.endswith('invalid'):
        scenario = line.split(' ')[1]
        msg = 'scenario {sc}: not all input validated yet'.format(sc=scenario)
        print(msg)
    else:
        raise ValueError(line)
    return scenario

def validate_scenario_from_visum(Visum):
    """
    Validate scenario

    Parameters
    ----------
    Visum : Visum-instance

    Returns
    -------
    scenarios : list of str
        the available scenarios
    """
    filetype_OtherOutputData = 89
    pythonpath = str(Visum.GetPath(filetype_OtherOutputData))

    filetype_OtherInputData = 88
    project_folder = str(Visum.GetPath(filetype_OtherInputData))

    scenario_name = Visum.Net.AttValue('ScenarioCode')

    # validate if scenario exists and is valid, or create and select a scenario
    scenario_name = validate_scenario(project_folder,
                                      scenario_name,
                                      pythonpath)

    Visum.Net.SetAttValue('ScenarioCode', scenario_name)


if __name__ == '__main__':
    r = get_scenarios_from_visum(Visum)
    raise ValueError(r)
    print(r)

##    parser = ArgumentParser(description="Parameter Importer")
##
##    parser.add_argument("-f", action="store",
##                        help="Projektordner mit XML-Projektdatei",
##                        dest="project_folder", default=None)
##
##    parser.add_argument("-s", action="store",
##                        help="angegebenes Szenario ausführen",
##                        dest="scenario_name", default=None)
##
##    parser.add_argument("--params", action="store",
##                       help="suche angegebene Parameter",
##                       dest="params", default=None, nargs='+')
##
##    parser.add_argument("--pythonpath", action="store",
##                      help="angegebenes Szenario ausführen",
##                      dest="pythonpath", default='python')
##
##    options = parser.parse_args()
##
##    res = get_scenarios(**options.__dict__)
##    print(res)
##
##    res = get_params(**options.__dict__)
##    print(res)

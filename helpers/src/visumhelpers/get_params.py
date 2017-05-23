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
from get_folders import get_folders


def get_params(project_folder, scenario_name, params,
               pythonpath=r''):
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

    pythonpath : str (optional)
        path of directory, where python executable resides

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
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         shell=True)

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
    pythonpath, project_folder = get_folders(Visum)

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
    pythonpath, project_folder = get_folders(Visum)

    return get_scenarios(project_folder, pythonpath)


def get_scenarios(project_folder, pythonpath=r'', **kwargs):
    """
    get available scenarios

    Parameters
    ----------
    project_folder : str
        path to the project folder

    pythonpath : str (optional)
        path to python executable directory
    Returns
    -------
    scenarios : list of str
        the available scenarios
    """
    project_xml_file = os.path.join(project_folder, 'project.xml')
    cmd = '{pythonpath} -m gui_vm.get_scenarios_from_config -o "{project_xml_file}"'
    c = subprocess.Popen(cmd.format(pythonpath=pythonpath,
                                    project_xml_file=project_xml_file),
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         shell=True)

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
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         shell=True)

    for i, scenario in enumerate(c.stdout.readlines()):
        print(i, scenario)

#def get_folders(Visum):
    #"""
    #return folders
    #"""
    #version = Visum.VersionNumber[:2]
    #visum_appdata = {'15': os.path.join('PTV Vision', 'PTV Visum 15'),
                     #}

    #p = os.path.join(
        #os.environ['APPDATA'],
        #visum_appdata.get(version,
                          #os.path.join('PTV Vision',
                                       #'PTV Visum {}'.format(version))),
    #)
    #pfd = os.path.join(p, 'ggr.pfd')
    #folders = {}
    #try:
        #with open(pfd) as f:
            #lines = f.readlines()
            #for line in lines:
                #l = line.strip().split('=')
                #if len(l) > 1:
                    #folders[l[0]] = l[1]
    #except IOError as e:
        #print('ggr.pfd not found in {}'.format(p))
        #raise e
    #try:
        #pythonpath = os.path.join(folders['ExecutableFolder'], 'python')
        #project_folder = folders['ProjectFolder']
    #except KeyError as e:
        #print('key not found in {pdf}'.format(pfd))
        #raise e
    #return pythonpath, project_folder


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
    pythonpath, project_folder = get_folders(Visum)
    return clone_scenario(project_folder, pythonpath, template, scenario_name)


def validate_scenario(project_folder,
                      scenario_name,
                      pythonpath=r'',
                      **kwargs):
    """
    validate available scenarios

    Parameters
    ----------
    project_folder : str
        path to the project folder
    scenario_name : str
        name of the scenario

    pythonpath : str (optional')
        path of directory where python executable resides
    Returns
    -------
    scenarios : list of str
        the available scenarios
    """
    project_xml_file = os.path.join(project_folder, 'project.xml')
    cmd = '{pythonpath} -m gui_vm.validate_scenario -f "{project_xml_file}" -s {sc}'
    fullcmd = cmd.format(pythonpath=pythonpath,
                         project_xml_file=project_xml_file,
                         sc=scenario_name)
    c = subprocess.Popen(fullcmd,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         shell=True)

    scenario = None
    run = None
    lines = c.stdout.readlines()
    for l in lines:
        line = l.strip()
        if line.startswith('no scenario selected'):
            print(line)
        if line.startswith('selected run:'):
            run = line.split(':')[1]
        if line.startswith('selected scenario:'):
            scenario = line.split(':')[1]
    if not scenario:
        print('No Scenario found')
    return scenario, run

def validate_scenario_from_visum(Visum, use_scenario_from_net=True):
    """
    Validate scenario

    Parameters
    ----------
    Visum : Visum-instance

    use_scenario_from_net : bool, optional(Default=True)

    Returns
    -------
    scenarios : list of str
        the available scenarios
    """
    pythonpath, project_folder = get_folders(Visum)

    if use_scenario_from_net:
        scenario_name = Visum.Net.AttValue('ScenarioCode')
    else:
        scenario_name = None

    # validate if scenario exists and is valid, or create and select a scenario
    scenario_name, run = validate_scenario(project_folder,
                                           scenario_name,
                                           pythonpath)

    #Visum.Net.SetAttValue('ScenarioCode', scenario_name)
    return scenario_name, run


if __name__ == '__main__':
    r = get_scenarios_from_visum(Visum)
    print(r)
    raise ValueError(r)

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
